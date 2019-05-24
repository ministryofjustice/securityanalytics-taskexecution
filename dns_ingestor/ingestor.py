import socket
import time
from dns_ingestor.host_to_scan import HostToScan


def ns_lookup(host):
    if host.endswith("."):
        host = host[:-1]
    # See https://docs.python.org/3/library/socket.html#socket.getaddrinfo
    # for magic indexes
    return [address[4][0] for address in socket.getaddrinfo(host, 0, 0, 0, 0)]


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

    def load_all(self):
        self._load_hosted_zones()
        while self.to_ingest:
            name, zone = self.to_ingest.popitem()
            self.ingested.add(name)
            self._process_hosted_zone(zone)

    def _load_hosted_zones(self):
        kwargs = {"MaxItems": "1000"}
        finished_listing_zones = False
        ingested = 0
        while not finished_listing_zones:
            list_resp = self.route53_client.list_hosted_zones(**kwargs)
            hosted_zones = list_resp["HostedZones"]
            for zone in hosted_zones:
                self.to_ingest[zone["Name"]] = zone
            ingested += len(hosted_zones)
            finished_listing_zones = not bool(list_resp["IsTruncated"])
            if not finished_listing_zones:
                kwargs["Marker"] = list_resp["NextMarker"]
        print(f"Discovered {ingested} hosted zones")

    def _process_hosted_zone(self, zone):
        kwargs = {"MaxItems": "1000"}
        finished_listing_resources = False
        ingested = 0
        while not finished_listing_resources:
            details_resp = self.route53_client.list_resource_record_sets(HostedZoneId=zone["Id"], **kwargs)
            for record in details_resp["ResourceRecordSets"]:
                ingested += self._dispatch_record(record)

            finished_listing_resources = not bool(details_resp["IsTruncated"])
            if not finished_listing_resources:
                kwargs["StartRecordName"] = details_resp["NextRecordName"]
                kwargs["StartRecordType"] = details_resp["NextRecordType"]
                if "NextRecordIdentifier" in details_resp:
                    kwargs["StartRecordIdentifier"] = details_resp["NextRecordIdentifier"]
                elif "StartRecordIdentifier" in kwargs:
                    del kwargs["StartRecordIdentifier"]

            # there is a 5 requests per second limit on aws for route53 calls
            # conservative here to ensure we finish the scan
            time.sleep(2.0/5.0)

        print(f"Ingested zone: {zone['Name']}, {ingested} records")

    def _dispatch_record(self, record):
        record_type = record["Type"]
        if record_type in self._record_type_handler.keys():
            return self._record_type_handler[record_type](record)
        else:
            return self._process_other_record(record)

    def _process_a_record(self, record):
        if "AliasTarget" in record:
            return self._process_alias_record(record)
        else:
            print(f"Ingested {record['Type']} record: {record['Name']}")
            records = record["ResourceRecords"]
            for resource in records:
                self.out_writer.write(HostToScan(resource["Value"], record["Name"]))
            return len(record)

    def _process_alias_record(self, record):
        print(f"Ingested ALIAS record: {record['Name']}")
        target = record["AliasTarget"]
        alias_zone = target["HostedZoneId"]
        record_count = 0
        if alias_zone in self.to_ingest.keys() or alias_zone in self.ingested:
            print(f"Ignoring alias to zone already being scanned {alias_zone} referred to by {record['Name']}")
        else:
            redirect_to = target["DNSName"]
            try:
                for ip in ns_lookup(redirect_to):
                    record_count += 1
                    self.out_writer.write(HostToScan(ip, record["Name"]))
                print(f"Resolved ip addresses of {redirect_to} an ALIAS of {record['Name']}")
            except socket.gaierror:
                print(f"Failed to resolve {redirect_to} an ALIAS of {record['Name']}")
        return record_count

    def _process_cname_record(self, record):
        print(f"Ingested {record['Type']} record: {record['Name']}")
        records = record["ResourceRecords"]
        record_count = 0
        for resource in records:
            # strip the dot
            redirect_to = resource["Value"]
            try:
                for ip in ns_lookup(redirect_to):
                    record_count += 1
                    self.out_writer.write(HostToScan(ip, record["Name"]))
                print(f"Resolved ip addresses of {redirect_to} an {record['Type']} of {record['Name']}")
            except socket.gaierror:
                print(f"Failed to resolve {redirect_to} a {record['Type']} of {record['Name']}")

        return len(record)

    def _process_other_record(self, record):
        if self.log_unhandled:
            print(f"Unhandled record {record['Type']}: {record}")
        return 0
