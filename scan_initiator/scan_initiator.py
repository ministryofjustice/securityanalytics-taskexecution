import os
import aioboto3
import time
from utils.lambda_decorators import ssm_parameters, async_handler
from boto3.dynamodb.conditions import Key
from asyncio import gather, run
from collections import namedtuple
from decimal import Decimal
import random
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.lambda_launcher import LambdaContext

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]

ssm_client = aioboto3.client("ssm", region_name=region)
sqs_client = aioboto3.client("sqs", region_name=region)
dynamo_resource = aioboto3.resource("dynamodb", region_name=region)

# ssm params
ssm_prefix = f"/{app_name}/{stage}"
SCAN_PLAN_TABLE = f"{ssm_prefix}/scheduler/dynamodb/id"
INDEX_NAME = f"{ssm_prefix}/scheduler/dynamodb/plan_index"
PLANNING_PERIOD_SECONDS = f"{ssm_prefix}/scheduler/config/period"
PLANNING_BUCKETS = f"{ssm_prefix}/scheduler/config/buckets"
SCAN_DELAY_QUEUE = f"{ssm_prefix}/scheduler/scan_delay_queue"


# This will pick a random delay across the period of the bucket this
# lambda fired to plan
async def queue_scans(batch, initiation_queue):
        print(f"Initiating batch of scans {batch}")
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


async def remove_plan_entries(batch, table):
    async with table.batch_writer() as writer:
        for address, ingested_time, _ in batch:
            await writer.delete_item(Key={
                "Address": address
            })


@ssm_parameters(
    ssm_client,
    SCAN_PLAN_TABLE,
    INDEX_NAME,
    PLANNING_PERIOD_SECONDS,
    PLANNING_BUCKETS,
    SCAN_DELAY_QUEUE
)
@async_handler()
async def initiate_scans(event, _):
    params = event['ssm_params']
    start_time = time.time()
    print(f"Querying all of the scans planned with a PlannedScanTime < {start_time}")
    scan_plan_table = dynamo_resource.Table(params[SCAN_PLAN_TABLE])

    plan_period = int(params[PLANNING_PERIOD_SECONDS])
    plan_buckets = int(params[PLANNING_BUCKETS])
    bucket_length = plan_period / plan_buckets

    pagination_params = {}
    scans_initiated = 0
    while True:
        scan_result = await scan_plan_table.scan(
            IndexName=params[INDEX_NAME],
            FilterExpression=Key("PlannedScanTime").lte(Decimal(start_time)),
            **pagination_params
        )

        plan_keys_and_delays = [
            (scan["Address"], scan["DnsIngestTime"], int(random.uniform(0, bucket_length)))
            for scan in scan_result["Items"]
        ]
        # SQS batch size max is 10, delete from the dynamodb in the same batches for ease
        batches = [plan_keys_and_delays[i:i + 10] for i in range(0, len(plan_keys_and_delays), 10)]

        # for each batch send to sqs and then delete from db. We may end up processing things multiple times in a
        # failure scenario e.g. when we scan and fail to delete, but we will never delete without a task going on to the
        # queue
        # N.B. We may want to change the condition used to determine when to remove the plan entries, it might be better
        # to remove it only after a scan is successfully finished. Avoiding that now, because it is more complex, and
        # because of chains of scans, and indexing in elastic, there is not really a good notion of a scan being
        # finished
        for batch in batches:
            await queue_scans(batch, params[SCAN_DELAY_QUEUE])
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
    try:
        xray_recorder.configure(context=LambdaContext())
        initiate_scans({}, namedtuple("context", ["loop"]))
    finally:
        run(clean_clients())