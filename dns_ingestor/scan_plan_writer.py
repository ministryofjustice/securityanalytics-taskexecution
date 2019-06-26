from dns_ingestor.host_to_scan import HostToScan
import datetime
import pytz
from asyncio import gather


# This class will write a HostToScan to the planned scan table
class PlannedScanDbWriter:
    def __init__(self, scan_plan_table, host_table, address_table, address_info_table, ingest_time, schedule):
        self.scan_plan_table = scan_plan_table
        self.host_table = host_table
        self.address_table = address_table
        self.address_info_table = address_info_table
        self.ingest_time = ingest_time
        self.ingest_time_string = datetime.datetime.fromtimestamp(int(ingest_time), pytz.utc).isoformat()
        self.ingest_time_string = self.ingest_time_string.replace('+00:00', 'Z')
        self.schedule = schedule
        self.update_scan_plan = "SET PlannedScanTime = :PlannedScanTime, " \
                                "DnsIngestTime = :DnsIngestTime"
        self.update_hosts = "SET Addresses = :Addresses"
        self.update_addresses = "SET Hosts = :Hosts"
        self.update_address_info = "SET LastDnsIngestTime = :LastDnsIngestTime, " \
                                   "NextPlannedScanTime = :NextPlannedScanTime"
        self.existing_hosts = None
        self.existing_addresses = None
        self.host_map = {}
        self.address_map = {}

    async def prepare(self):
        # Nothing needed right now, but this could be a useful extension point later
        pass

    async def write(self, host):
        if not isinstance(host, HostToScan):
            raise ValueError(f"Incorrect type {type(host)}, expecting {HostToScan}")
        # update the resolved entity sets
        self._merge_into_resolved_map(self.address_map, host.address, host.host)
        self._merge_into_resolved_map(self.host_map, host.host, host.address)

    async def commit(self):
        await self._write_resolved_addresses()
        await self._write_resolved_hosts()

    @staticmethod
    async def _get_existing_entities(address_table, key):
        response = await address_table.scan()
        data = [x[key] for x in response['Items']]
        while 'LastEvaluatedKey' in response:
            response = await address_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend([x[key] for x in response['Items']])
        return data

    def _merge_into_resolved_map(self, entity_map, from_entity, to_entity):
        resolved_entities = entity_map.get(from_entity, set())
        resolved_entities.add(to_entity)
        entity_map[from_entity] = resolved_entities

    async def _write_resolved_addresses(self):
        for address, hosts in self.address_map.items():
            # N.B. we are pulling from a uniform distribution, we may or may not use this sample
            # However that will still leave us with the planned scans uniformly distributed
            planned_slot = next(self.schedule)

            await gather(
                # Update the table scan plan
                self.scan_plan_table.update_item(
                    Key={"Address": address},
                    UpdateExpression=self.update_scan_plan,
                    ExpressionAttributeValues={
                        ":PlannedScanTime": int(planned_slot),
                        ":DnsIngestTime": int(self.ingest_time)
                    }
                ),
                # Update the table of addresses to hosts, this is only used for visualisations
                # in Kibana
                self.address_table.update_item(
                    Key={
                        "Address": address,
                        "DnsIngestTime": int(self.ingest_time)
                    },
                    UpdateExpression=self.update_addresses,
                    ExpressionAttributeValues={
                        ":Hosts": hosts
                    }
                ),
                # Update the info about last time this address was ingested/resolved
                self.address_info_table.update_item(
                    Key={"Address": address},
                    UpdateExpression=self.update_address_info,
                    ExpressionAttributeValues={
                        ":LastDnsIngestTime": int(self.ingest_time),
                        ":NextPlannedScanTime": int(planned_slot)
                    }
                )
            )

    async def _write_resolved_hosts(self):
        for host, addresses in self.host_map.items():

            # Update the table of hosts to addresses, this is only used for visualisations
            # in Kibana
            await self.host_table.update_item(
                Key={
                    "Host": host,
                    "DnsIngestTime": int(self.ingest_time)
                },
                UpdateExpression=self.update_hosts,
                ExpressionAttributeValues={
                    ":Addresses": addresses
                }
            )
