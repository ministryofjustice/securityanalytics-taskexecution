from dns_ingestor.host_to_scan import HostToScan
import datetime
import pytz


# This class will write a HostToScan to the planned scan table
class PlannedScanDbWriter:
    def __init__(self, db_table, ingest_time, schedule):
        self.table = db_table
        self.ingest_time = ingest_time
        self.ingest_time_string = datetime.datetime.fromtimestamp(int(ingest_time), pytz.utc).isoformat()
        self.schedule = schedule
        self.update_expr = "SET #Hosts = list_append(if_not_exists(#Hosts, :empty_list), :Host), " \
                           "PlannedScanTime = if_not_exists(#PlannedScanTime, :PlannedScanTime)"

    async def write(self, host):
        if not isinstance(host, HostToScan):
            raise ValueError(f"Incorrect type {type(host)}, expecting {HostToScan}")

        # N.B. we are pulling from a uniform distribution, we may or may not use this sample
        # However that will still leave us with the planned scans uniformly distributed
        planned_slot = next(self.schedule)

        await self.table.update_item(
            Key={"Address": host.address, "DnsIngestTime": str(self.ingest_time)},
            UpdateExpression=self.update_expr,
            ExpressionAttributeNames={
                "#Hosts": "HostsResolvingToAddress",
                "#PlannedScanTime": "PlannedScanTime"
            },
            ExpressionAttributeValues={
                ":Host": [host.host],
                ":PlannedScanTime": planned_slot,
                ":empty_list": []
            },
            ReturnValues="UPDATED_NEW"
        )
