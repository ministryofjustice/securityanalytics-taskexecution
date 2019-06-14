import os
import aioboto3
import time
from utils.lambda_decorators import ssm_parameters, async_handler
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from asyncio import gather

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]

ssm_client = aioboto3.client("ssm", region_name=region)
sqs_client = aioboto3.client("sqs", region_name=region)
dynamo_resource = aioboto3.resource("dynamodb", region_name=region)

# ssm params
ssm_prefix = f"/{app_name}/{stage}"
SCAN_PLAN_TABLE = f"{ssm_prefix}/scheduler/dynamodb/scans_planned/id"
SCAN_INFO_TABLE = f"{ssm_prefix}/scheduler/dynamodb/address_info/id"
INDEX_NAME = f"{ssm_prefix}/scheduler/dynamodb/scans_planned/plan_index"
PLANNING_PERIOD_SECONDS = f"{ssm_prefix}/scheduler/config/period"
PLANNING_BUCKETS = f"{ssm_prefix}/scheduler/config/buckets"
SCAN_DELAY_QUEUE = f"{ssm_prefix}/scheduler/scan_delay_queue"


# This will pick a random delay across the period of the bucket this
# lambda fired to plan
async def queue_scans(batch, initiation_queue, scan_info_table):
    print(f"Initiating batch of scans {batch}")
    queue_time = time.time()
    await sqs_client.send_message_batch(
        QueueUrl=initiation_queue,
        Entries=[
            {
                # IP4 addresses have . and IP6 have : replace those with -
                "Id": address.replace(".", "-").replace(":", "-"),
                "DelaySeconds": delay,
                "MessageBody": f"{{\"CloudWatchEventHosts\":[\"{address}\"]}}"
            }
            for address, _, delay in batch
        ]
    )

    for address, ingested_time, _ in batch:
        await scan_info_table.update_item(
            Key={"Address": address},
            UpdateExpression="SET LastPlannedScanQueued = :LastPlannedScanQueued",
            ExpressionAttributeValues={
                ":LastPlannedScanQueued": int(queue_time)
            }
        )


async def remove_plan_entries(batch, table):
    async with table.batch_writer() as writer:
        for address, ingested_time, _ in batch:
            await writer.delete_item(Key={"Address": address})


@ssm_parameters(
    ssm_client,
    SCAN_PLAN_TABLE,
    SCAN_INFO_TABLE,
    INDEX_NAME,
    PLANNING_PERIOD_SECONDS,
    PLANNING_BUCKETS,
    SCAN_DELAY_QUEUE
)
@async_handler()
async def initiate_scans(event, _):
    params = event['ssm_params']

    plan_period = int(params[PLANNING_PERIOD_SECONDS])
    plan_buckets = int(params[PLANNING_BUCKETS])
    bucket_length = plan_period / plan_buckets

    # we take now and look a whole bucket in the future for tasks to queue
    now = time.time()
    last_task_time_to_queue = now + bucket_length
    print(f"Querying all of the scans planned with a PlannedScanTime < {last_task_time_to_queue}")
    scan_plan_table = dynamo_resource.Table(params[SCAN_PLAN_TABLE])
    scan_info_table = dynamo_resource.Table(params[SCAN_INFO_TABLE])
    scan_delay_queue = params[SCAN_DELAY_QUEUE]

    pagination_params = {}
    scans_initiated = 0
    while True:
        scan_result = await scan_plan_table.scan(
            IndexName=params[INDEX_NAME],
            FilterExpression=Key("PlannedScanTime").lte(Decimal(last_task_time_to_queue)),
            **pagination_params
        )

        plan_keys_and_delays = [
            # calc the delay between now and the time to scan, can't have negative delay
            (scan["Address"], scan["DnsIngestTime"], int(max(0, float(scan["PlannedScanTime"]) - now)))
            for scan in scan_result["Items"]
        ]

        # SQS batch size max is 10, delete from the dynamodb in the same batches for ease
        batches = [plan_keys_and_delays[i:i + 10] for i in range(0, len(plan_keys_and_delays), 10)]
        # for each batch send to sqs and then delete from db. We may end up processing things multiple
        # times in a failure scenario e.g. when we scan and fail to delete, but we will never delete
        # without a task going on to the queue
        # N.B. We may want to change the condition used to determine when to remove the plan entries,
        # it might be better to remove it only after a scan is successfully finished. Avoiding that now,
        # because it is more complex. Because of chains of scans, and indexing in elastic, there is
        # not really a good notion of a scan being finished
        for batch in batches:
            await queue_scans(batch, scan_delay_queue, scan_info_table)
            scans_initiated += len(batch)
            await remove_plan_entries(batch, scan_plan_table)

        if "LastEvaluatedKey" in scan_result:
            pagination_params["ExclusiveStartKey"] = scan_result["LastEvaluatedKey"]
        else:
            break

    print(f"Completed queuing {scans_initiated} scan initiation messages")


# Test cases can use this to clean up the clients
async def clean_clients():
    return await gather(
        ssm_client.close(),
        sqs_client.close(),
        dynamo_resource.close()
    )

# For developer test use only
if __name__ == "__main__":
    from asyncio import run
    from aws_xray_sdk.core import xray_recorder
    from aws_xray_sdk.core.lambda_launcher import LambdaContext
    try:
        xray_recorder.configure(context=LambdaContext())
        initiate_scans({}, type("Context", (), {"loop": None})())
    finally:
        run(clean_clients())
