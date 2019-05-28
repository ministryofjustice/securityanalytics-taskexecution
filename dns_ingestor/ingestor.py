from asyncio import get_running_loop, gather
import time
from socket import gaierror
from dns_ingestor.host_to_scan import HostToScan


async def ns_lookup(host):
    if host.endswith("."):
        host = host[:-1]
    # See https://docs.python.org/3/library/socket.html#socket.getaddrinfo
    # for magic indexes
    loop = get_running_loop()
    return [address[4][0] for address in await loop.getaddrinfo(host, 0)]


class DnsIngestor:
    def __init__(self, route53_client, out_writer, log_unhandled):
        self.out_writer = out_writer
        self._record_type_handler = {
            "A": self._process_a_record,
            "AAAA": self._process_a_record,
            "CNAME": self._process_cname_record
            # TODO any requirements to scan e.g mx records?
        }
        self.ingested = set()
        self.to_ingest = {}
        self.route53_client = route53_client
        self.log_unhandled = log_unhandled

    async def load_all(self):
        await self._load_hosted_zones()
        total = 0
        while self.to_ingest:
            name, zone = self.to_ingest.popitem()
            self.ingested.add(name)
            total += await self._process_hosted_zone(zone)
        print(f"Finished ingesting all dns records {total} hosts found")

    async def _load_hosted_zones(self):
        kwargs = {"MaxItems": "1000"}
        finished_listing_zones = False
        ingested = 0
        while not finished_listing_zones:
            list_resp = await self.route53_client.list_hosted_zones(**kwargs)
            hosted_zones = list_resp["HostedZones"]
            for zone in hosted_zones:
                self.to_ingest[zone["Name"]] = zone
            ingested += len(hosted_zones)
            finished_listing_zones = not bool(list_resp["IsTruncated"])
            if not finished_listing_zones:
                kwargs["Marker"] = list_resp["NextMarker"]
        print(f"Discovered {ingested} hosted zones")

    async def _process_hosted_zone(self, zone):
        kwargs = {"MaxItems": "1000"}
        finished_listing_resources = False
        db_writes = []
        while not finished_listing_resources:
            details_resp = await self.route53_client.list_resource_record_sets(HostedZoneId=zone["Id"], **kwargs)

            db_writes += [
                self._dispatch_record(record) for record in details_resp["ResourceRecordSets"]
            ]

            # this block updates the paging details for the next list_resource_record_sets call
            finished_listing_resources = not bool(details_resp["IsTruncated"])
            if not finished_listing_resources:
                kwargs["StartRecordName"] = details_resp["NextRecordName"]
                kwargs["StartRecordType"] = details_resp["NextRecordType"]
                if "NextRecordIdentifier" in details_resp:
                    kwargs["StartRecordIdentifier"] = details_resp["NextRecordIdentifier"]
                elif "StartRecordIdentifier" in kwargs:
                    del kwargs["StartRecordIdentifier"]

            # there is a 5 requests per second limit on aws for route53 calls
            time.sleep(1.0/5.0)

        print(f"Ingested zone: {zone['Name']}, {len(db_writes)} records")
        for writes in db_writes:
            await writes
        return len(db_writes)

    async def _dispatch_record(self, record):
        record_type = record["Type"]
        if record_type in self._record_type_handler.keys():
            return await self._record_type_handler[record_type](record)
        else:
            return await self._process_other_record(record)

    async def _scan_hosts(self, hosts_to_scan):
        return gather(*[
            self.out_writer.write(host_to_scan) for host_to_scan in hosts_to_scan
        ])

    async def _process_a_record(self, record):
        if "AliasTarget" in record:
            return await self._process_alias_record(record)
        else:
            print(f"Ingested {record['Type']} record: {record['Name']}")
            records = record["ResourceRecords"]
            result = await self._scan_hosts([
                HostToScan(resource["Value"], record["Name"]) for resource in records
            ])
            return result

    async def _process_alias_record(self, record):
        print(f"Ingested ALIAS record: {record['Name']}")
        target = record["AliasTarget"]
        alias_zone = target["HostedZoneId"]
        writes = []
        if alias_zone in self.to_ingest.keys() or alias_zone in self.ingested:
            print(f"Ignoring alias to zone already being scanned {alias_zone} referred to by {record['Name']}")
        else:
            redirect_to = target["DNSName"]
            try:
                writes += await self._scan_hosts([
                    HostToScan(ip, record["Name"]) for ip in await ns_lookup(redirect_to)
                ])
                print(f"Resolved ip addresses of {redirect_to} an ALIAS of {record['Name']}")
            except (RuntimeError, gaierror):
                print(f"Failed to resolve {redirect_to} an ALIAS of {record['Name']}")
        return writes

    async def _process_cname_record(self, record):
        print(f"Ingested {record['Type']} record: {record['Name']}")
        records = record["ResourceRecords"]
        writes = []
        for resource in records:
            # strip the dot
            redirect_to = resource["Value"]
            try:

                writes += await self._scan_hosts([
                    HostToScan(ip, record["Name"]) for ip in await ns_lookup(redirect_to)
                ])
                print(f"Resolved ip addresses of {redirect_to} an {record['Type']} of {record['Name']}")
            except (RuntimeError, gaierror):
                print(f"Failed to resolve {redirect_to} a {record['Type']} of {record['Name']}")

        return writes

    async def _process_other_record(self, record):
        if self.log_unhandled:
            print(f"Unhandled record {record['Type']}: {record}")
        return []
