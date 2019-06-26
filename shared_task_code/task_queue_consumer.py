import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from datetime import datetime
import subprocess


class TaskQueueConsumer:
    region = os.environ["REGION"]
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"
    ssm_client = boto3.client("ssm", region_name=region)

    RESULTS = f"{ssm_prefix}/tasks/{task_name}/s3/results/id"

    def get_ssm_params(self, ssm_client, param_names):
        ret = self.ssm_client.get_parameters(Names=param_names)
        params = ret['Parameters']
        return {p['Name']: p['Value'] for p in params}

    def __init__(self, event):
        self.event = event

    def run_scan(self, scan, message_id):
        # Use this format to have uniformly named files in S3
        date_string = f"{datetime.now():%Y-%m-%dT%H%M%S%Z}"
        s3file = f"{message_id}-{date_string}-{self.task_name}.txt"

        results_filename = f"/tmp/{s3file}"
        scan['start_time'] = f"{datetime.now():%Y-%m-%dT%H:%M:%S}Z"
        if self.func_taskcode != None:
            self.func_taskcode(self.event, scan, message_id, results_filename, '/tmp/')
        scan['end_time'] = f"{datetime.now():%Y-%m-%dT%H:%M:%S}Z"
        subprocess.check_output(f'cd /tmp;tar -czvf "{s3file}.tar.gz" "{s3file}"', shell=True)
        s3 = boto3.resource("s3", region_name=self.region)

        s3.meta.client.upload_file(
            f"/tmp/{s3file}.tar.gz",
            self.event["ssm_params"][self.RESULTS],
            f"{s3file}.tar.gz",
            ExtraArgs={'ServerSideEncryption': "AES256", 'Metadata': scan})

    def process_records(self, task_func, validate_data, task_code):
        self.func_validatedata = validate_data
        self.func_taskcode = task_code
        for record in self.event["Records"]:
            try:
                scan = loads(record["body"])
            except:
                scan = record["body"]
                pass
            message_id = f"{record['messageId']}"
            if self.func_validatedata != None:
                # validatedata should validate the data, and return a cleaned/destructured
                # version of it, e.g. for nmap scanner there's a case where there are a list
                # of things to scan - so in this case, the string 'scan', could return as
                # an array of strings
                (valid, scan) = self.func_validatedata(self.event, scan, message_id)
            else:
                valid = True
            if valid:
                if isinstance(scan, list):
                    for scanitem in scan:
                        task_func(scanitem, message_id)
                else:
                    task_func(scan, message_id)

    def start(self, validate_data=None, task_code=None):
        # Pass in variables by name for:
        # ValidateData=func() - optional (validates the event data)
        # TaskCode=func() - the code to execute for this task
        self.event['ssm_params'] = self.get_ssm_params(self.ssm_client, [self.RESULTS])

        self.process_records(self.run_scan, validate_data, task_code)
