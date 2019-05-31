from asyncio import get_event_loop
from socket import gaierror
from dns_ingestor.host_to_scan import HostToScan


# Used to resolve c names and aws aliases
async def ns_lookup(host):
    if host.endswith("."):
        host = host[:-1]
    # See https://docs.python.org/3/library/socket.html#socket.getaddrinfo
    # for magic indexes
    loop = get_event_loop()
    addresses = await loop.getaddrinfo(host, 0)
    print(addresses)
    short_addresses = [address[4][0] for address in addresses]
    dedupped = list(dict.fromkeys(short_addresses))
    print(dedupped)
    return dedupped


class RecordResolver:
    def __init__(self, known_zones, log_unhandled):
        self.log_unhandled = log_unhandled
        self.known_zones = known_zones
        self._record_type_handler = {
            "A": self._resolve_a_record,
            "AAAA": self._resolve_a_record,
            "CNAME": self._resolve_cname_record
            # TODO any requirements to scan e.g mx records?
        }
        self.ips_resolved = 0

    async def resolve(self, record):
        record_type = record["Type"]
        if record_type in self._record_type_handler.keys():
            result = await self._record_type_handler[record_type](record)
        else:
            result = await self._resolve_other_record(record)
        return result

    async def _resolve_a_record(self, record):
        if "AliasTarget" in record:
            return await self._resolve_alias_record(record)
        else:
            # print(f"Ingested {record['Type']} record: {record['Name']}")
            return self._ips_resolved([
                HostToScan(resource["Value"], record["Name"])
                for resource in record["ResourceRecords"]
            ])

    async def _resolve_alias_record(self, record):
        target = record["AliasTarget"]
        alias_zone = target["HostedZoneId"]
        if alias_zone in self.known_zones.keys():
            # print(f"Ignoring alias to zone already being scanned {alias_zone} referred to by {record['Name']}")
            return []
        else:
            return await self._resolve_using_ns_lookup(record, [target["DNSName"]], "ALIAS")

    async def _resolve_cname_record(self, record):
        return await self._resolve_using_ns_lookup(
            record,
            [resource["Value"] for resource in record["ResourceRecords"]],
            record["Type"]
        )

    async def _resolve_using_ns_lookup(self, record, redirects, record_type):
        # print(f"Ingested {record_type} record: {record['Name']}")
        to_scan = []
        for redirect_to in redirects:
            try:
                to_scan += [HostToScan(ip, record["Name"]) for ip in await ns_lookup(redirect_to)]
                # print(f"Resolved ip addresses of {redirect_to} a(n) {record_type} of {record['Name']}")
            except gaierror:
                # print(f"Unable to resolve {redirect_to} a(n) {record_type} of {record['Name']}")
                pass

        return self._ips_resolved(to_scan)

    async def _resolve_other_record(self, record):
        if self.log_unhandled:
            # print(f"Unhandled record {record['Type']}: {record}")
            pass
        return []

    def _ips_resolved(self, hosts_to_scan):
        self.ips_resolved += len(hosts_to_scan)
        return hosts_to_scan
