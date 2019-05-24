from dns_ingestor.host_to_scan import HostToScan
import datetime
import pytz


# This class will write a HostToScan to the planned scan table
class PlannedScanDbWriter:
    def __init__(self, db_table, ingest_time, scheduler):
        self.table = db_table
        self.ingest_time = ingest_time
        self.ingest_time_string = datetime.datetime.fromtimestamp(int(ingest_time), pytz.utc).isoformat()
        self.scheduler = scheduler
        self.update_expr = "SET #Hosts = list_append(if_not_exists(#Hosts, :empty_list), :Host), " \
                           "PlannedScanTime = if_not_exists(#PlannedScanTime, :PlannedScanTime)"

    def write(self, host):
        if not isinstance(host, HostToScan):
            raise ValueError(f"Incorrect type {type(host)}, expecting {HostToScan}")

        planned_slot = self.scheduler.next_planned_slot()
        response = self.table.update_item(
            Key={'Address': host.address, 'DnsIngestTime': str(self.ingest_time)},
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
        # we asked dynamo to return updated attributes only
        # when we see that our planned scan time was used, we need to tell the scheduler
        # use the next value, N.B. it seems to return the old value even when not changed
        # because there is a mention in update expression, so need to check values equal as well
        resp_attrs = response["Attributes"]
        if "PlannedScanTime" in resp_attrs and planned_slot == resp_attrs["PlannedScanTime"]:
            self.scheduler.use_slot()
