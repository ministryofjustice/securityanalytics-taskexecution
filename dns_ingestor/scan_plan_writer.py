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
        self.schedule = schedule
        self.update_scan_plan = "ADD #Hosts :Host " \
                                "SET PlannedScanTime = :PlannedScanTime, " \
                                "DnsIngestTime = :DnsIngestTime"
        self.update_hosts = "ADD #Addresses :Address"
        self.update_addresses = "ADD #Hosts :Host"
        self.update_address_info = "SET LastDnsIngestTime = :LastDnsIngestTime, " \
                                   "NextPlannedScanTime = :NextPlannedScanTime"

    async def write(self, host):
        if not isinstance(host, HostToScan):
            raise ValueError(f"Incorrect type {type(host)}, expecting {HostToScan}")

        # N.B. we are pulling from a uniform distribution, we may or may not use this sample
        # However that will still leave us with the planned scans uniformly distributed
        planned_slot = next(self.schedule)

        await gather(
            # Update the table scan plan
            self.scan_plan_table.update_item(
                Key={"Address": host.address},
                UpdateExpression=self.update_scan_plan,
                ExpressionAttributeNames={
                    "#Hosts": "HostsResolvingToAddress"
                },
                ExpressionAttributeValues={
                    ":Host": set([host.host]),
                    ":PlannedScanTime": int(planned_slot),
                    ":DnsIngestTime": int(self.ingest_time)
                }
            ),
            # Update the table of hosts to addresses, this is only used for visualisations
            # in Kibana
            self.host_table.update_item(
                Key={
                    "Host": host.host,
                    "DnsIngestTime": int(self.ingest_time)
                },
                UpdateExpression=self.update_hosts,
                ExpressionAttributeNames={
                    "#Addresses": "Addresses",
                },
                ExpressionAttributeValues={
                    ":Address": set([host.address])
                }
            ),
            # Update the table of addresses to hosts, this is only used for visualisations
            # in Kibana
            self.address_table.update_item(
                Key={
                    "Address": host.address,
                    "DnsIngestTime": int(self.ingest_time)
                },
                UpdateExpression=self.update_addresses,
                ExpressionAttributeNames={
                    "#Hosts": "Hosts",
                },
                ExpressionAttributeValues={
                    ":Host": set([host.host])
                }
            ),
            # Update the info about last time this address was ingested/resolved
            self.address_info_table.update_item(
                Key={"Address": host.address},
                UpdateExpression=self.update_address_info,
                ExpressionAttributeValues={
                    ":LastDnsIngestTime": int(self.ingest_time),
                    ":NextPlannedScanTime": int(planned_slot)
                }
            )
        )
