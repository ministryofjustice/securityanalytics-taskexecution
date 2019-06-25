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
    ecs_client = boto3.client("ecs", region_name=region)

    PRIVATE_SUBNETS = f"{ssm_prefix}/vpc/using_private_subnets"
    SUBNETS = f"{ssm_prefix}/vpc/subnets/instance"
    CLUSTER = f"{ssm_prefix}/ecs/cluster"
    RESULTS = f"{ssm_prefix}/tasks/{task_name}/s3/results/id"
    SECURITY_GROUP = f"{ssm_prefix}/tasks/{task_name}/security_group/id"
    IMAGE_ID = f"{ssm_prefix}/tasks/{task_name}/image/id"

    def get_ssm_params(self, ssm_client, param_names):
        ret = self.ssm_client.get_parameters(Names=param_names)
        params = ret['Parameters']
        return {p['Name']: p['Value'] for p in params}

    def __init__(self, event):
        self.event = event

    def submit_ecs_task(self, event, task_params, message_id):
        ssm_params = event["ssm_params"]
        private_subnet = "true" == ssm_params[self.PRIVATE_SUBNETS]
        network_configuration = {
            "awsvpcConfiguration": {
                "subnets": ssm_params[self.SUBNETS].split(","),
                "securityGroups": [ssm_params[self.SECURITY_GROUP]],
                "assignPublicIp": "DISABLED" if private_subnet else "ENABLED"
            }
        }
        env_obj = [
            {
                "name": "TASK_INPUT",
                "value": task_params['target']
            },
            {
                "name": "MESSAGE_ID",
                "value": message_id
            },
            {
                "name": "RESULTS_BUCKET",
                "value": ssm_params[self.RESULTS]
            },
            {
                "name": "S3_METADATA",
                "value": f"scan_end_time={task_params['scan_end_time']},address={task_params['address']},address_type={task_params['address_type']}""

        }]

        if 'env_vars' in task_params:
            env_obj += task_params['env_vars']
            
        ecs_params = {
            "cluster": ssm_params[self.CLUSTER],
            "networkConfiguration": network_configuration,
            "taskDefinition": ssm_params[self.IMAGE_ID],
            "launchType": "FARGATE",
            "overrides": {
                "containerOverrides": [{
                    "name": self.task_name,
                    "environment": env_obj
                }]
            }
        }
        print(f"Submitting task: {dumps(ecs_params)}")
        task_response = self.ecs_client.run_task(**ecs_params)
        print(f"Submitted scanning task: {dumps(task_response)}")

        failures = task_response["failures"]
        if len(failures) != 0:
            raise RuntimeError(
                f"ECS task failed to start {dumps(failures)}")

    def start(self, validate_data=None, task_code=None):
        # Pass in variables by name for:
        # ValidateData=func() - optional (validates the event data)
        # TaskCode=func() - the code to execute for this task
        self.event['ssm_params'] = self.get_ssm_params(
            self.ssm_client, [self.PRIVATE_SUBNETS,
                              self.SUBNETS, self.CLUSTER, self.RESULTS, self.SECURITY_GROUP, self.IMAGE_ID])

        self.func_validatedata = validate_data
        self.func_taskcode = task_code
        for record in self.event["Records"]:
            scan = record["body"]
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
