import os
import aioboto3
from utils.lambda_decorators import ssm_parameters, async_handler
import time
from timeit import default_timer as timer
from dns_ingestor.scheduler import Scheduler
from dns_ingestor.scan_plan_writer import PlannedScanDbWriter
from dns_ingestor.ingestor import DnsIngestor
from asyncio import get_event_loop
from collections import namedtuple

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]

ssm_client = aioboto3.client("ssm", region_name=region)
sts_client = aioboto3.client("sts", region_name=region)
dynamo_resource = aioboto3.resource("dynamodb", region_name=region)


# ssm params
ssm_prefix = f"/{app_name}/{stage}"
ROUTE53_ROLE = f"{ssm_prefix}/scheduler/route53/role/arn"
SCAN_PLAN_TABLE = f"{ssm_prefix}/scheduler/dynamodb/id"
PLANNING_PERIOD_SECONDS = f"{ssm_prefix}/scheduler/config/period"
PLANNING_BUCKETS = f"{ssm_prefix}/scheduler/config/buckets"
LOG_UNHANDLED = f"{ssm_prefix}/scheduler/config/log_unhandled"


async def get_route53_client(role):
    route53_role = await sts_client.assume_role(RoleArn=role, RoleSessionName="ScanPlanSession")
    assumed_creds = route53_role["Credentials"]
    return aioboto3.client(
        "route53",
        aws_access_key_id=assumed_creds['AccessKeyId'],
        aws_secret_access_key=assumed_creds['SecretAccessKey'],
        aws_session_token=assumed_creds['SessionToken']
    )


@ssm_parameters(
    ssm_client,
    ROUTE53_ROLE,
    SCAN_PLAN_TABLE,
    PLANNING_PERIOD_SECONDS,
    PLANNING_BUCKETS,
    LOG_UNHANDLED
)
@async_handler
async def ingest_dns(event, _):
    params = event['ssm_params']
    start = timer()
    ingest_time = time.time()

    scheduler = Scheduler(
        ingest_time,
        int(params[PLANNING_PERIOD_SECONDS]),
        int(params[PLANNING_BUCKETS])
    )
    scan_plan = dynamo_resource.Table(params[SCAN_PLAN_TABLE])
    writer = PlannedScanDbWriter(
        scan_plan,
        ingest_time,
        scheduler
    )
    route53_client = await get_route53_client(params[ROUTE53_ROLE])
    log_unhandled = params[LOG_UNHANDLED].lower() == "true"

    await DnsIngestor(
        route53_client,
        writer,
        log_unhandled
    ).load_all()

    end = timer()
    print(f"Ingested all zones in {end-start}s")
