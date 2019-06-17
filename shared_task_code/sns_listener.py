import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from datetime import datetime
import subprocess


class SNSListener:
    region = os.environ["REGION"]
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"
    ssm_client = boto3.client("ssm", region_name=region)
    sqs_client = boto3.client("sqs", region_name=region)
    SQS_PUSH_URL = f"{ssm_prefix}/tasks/{task_name}/task_queue/url"

    def get_ssm_params(self, ssm_client, *param_names):
        ret = self.ssm_client.get_parameters(Names=[*param_names])
        params = ret['Parameters']
        return {p['Name']: p['Value'] for p in params}

    def __init__(self, event):
        self.event = event

    def sendToSQS(self, json_data):
        print(json_data)
        return self.sqs_client.send_message(
            QueueUrl=self.event["ssm_params"][self.SQS_PUSH_URL],
            MessageBody=dumps(json_data)
        )

    def start(self, PassToQueue=None):

        self.event['ssm_params'] = self.get_ssm_params(self.ssm_client, self.SQS_PUSH_URL)
        for record in self.event["Records"]:
            print(record)
            PassToQueue(self.event, record["Sns"], self)
