import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from datetime import datetime
import subprocess


class ECSTaskQueueConsumer:
    region = os.environ["REGION"]
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"
    ssm_client = boto3.client("ssm", region_name=region)

    RESULTS = f"{ssm_prefix}/tasks/{task_name}/s3/results/id"

    def get_ssm_params(self, ssm_client, *param_names):
        ret = self.ssm_client.get_parameters(Names=[*param_names])
        params = ret['Parameters']
        return {p['Name']: p['Value'] for p in params}

    def __init__(self, event):
        self.event = event

    def submit_ecs_task(self, event, task_params, message_id):
        ssm_params = event["ssm_params"]
        private_subnet = "true" == ssm_params[PRIVATE_SUBNETS]
        network_configuration = {
            "awsvpcConfiguration": {
                "subnets": ssm_params[SUBNETS].split(","),
                "securityGroups": [ssm_params[SECURITY_GROUP]],
                "assignPublicIp": "DISABLED" if private_subnet else "ENABLED"
            }
        }
        ecs_params = {
            "cluster": ssm_params[CLUSTER],
            "networkConfiguration": network_configuration,
            "taskDefinition": ssm_params[IMAGE_ID],
            "launchType": "FARGATE",
            "overrides": {
                "containerOverrides": [{
                    "name": task_name,
                    "environment": [
                        # TODO The only bit of this file that isn't going to be the same for other
                        # task queue executors, is this bit that maps the request body to some env vars
                        # Extract the common code into a layer exported by the task-execution project
                        # {
                        #     "name": "NMAP_TARGET_STRING",
                        #             "value": sanitise_nmap_target(host.strip())
                        # },
                        {
                            "name": "TASK_PARAMS",
                            "value": task_params
                        },
                        {
                            "name": "MESSAGE_ID",
                                    "value": message_id
                        },
                        {
                            "name": "RESULTS_BUCKET",
                                    "value": ssm_params[RESULTS]
                        }]
                }]
            }
        }
        print(f"Submitting task: {dumps(ecs_params)}")
        task_response = ecs_client.run_task(**ecs_params)
        print(f"Submitted scanning task: {dumps(task_response)}")

        failures = task_response["failures"]
        if len(failures) != 0:
            raise RuntimeError(
                f"ECS task failed to start {dumps(failures)}")

        def run_scan(self, scan, message_id):
            # Use this format to have uniformly named files in S3
            date_string = f"{datetime.now():%Y-%m-%dT%H%M%S%Z}"
            s3file = f"{message_id}-{date_string}-{self.task_name}.txt"

            results_filename = f"/tmp/{s3file}"

            if self.func_taskcode != None:
                self.func_taskcode(self.event, scan, message_id, results_filename, '/tmp/')

            subprocess.check_output(f'cd /tmp;tar -czvf "{s3file}.tar.gz" "{s3file}"', shell=True)
            s3 = boto3.resource("s3", region_name=self.region)
            s3.meta.client.upload_file(
                f"/tmp/{s3file}.tar.gz",
                self.event["ssm_params"][self.RESULTS],
                f"{s3file}.tar.gz",
                ExtraArgs={'ServerSideEncryption': "AES256", 'Metadata': scan})

    def start(self, ValidateData=None, TaskCode=None):
        # Pass in variables by name for:
        # ValidateData=func() - optional (validates the event data)
        # TaskCode=func() - the code to execute for this task
        self.event['ssm_params'] = self.get_ssm_params(self.ssm_client, self.RESULTS)

        self.func_validatedata = ValidateData
        self.func_taskcode = TaskCode
        for record in self.event["Records"]:
            scan = loads(record["body"])
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
                        self.submit_ecs_task(self.event, scanitem, message_id)
                else:
                    self.submit_ecs_task(self.event, scan, message_id)
