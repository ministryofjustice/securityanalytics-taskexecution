import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from datetime import datetime
import subprocess
from shared_task_code.task_queue_consumer import TaskQueueConsumer


class ECSTaskQueueConsumer(TaskQueueConsumer):

    def __init__(self, event):
        self.ecs_client = boto3.client("ecs", region_name=self.region)

        self.PRIVATE_SUBNETS = f"{self.ssm_prefix}/vpc/using_private_subnets"
        self.SUBNETS = f"{self.ssm_prefix}/vpc/subnets/instance"
        self.CLUSTER = f"{self.ssm_prefix}/ecs/cluster"
        self.SECURITY_GROUP = f"{self.ssm_prefix}/tasks/{self.task_name}/security_group/id"
        self.IMAGE_ID = f"{self.ssm_prefix}/tasks/{self.task_name}/image/id"
        self.event = event

    def submit_ecs_task(self, task_params, message_id):
        ssm_params = self.event["ssm_params"]
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
            }]

        if 'address' in task_params:
            # this is usually only valid for secondary scans
            env_obj += [{
                # use comma format to allow other metadata fields to be easily appended in the docker task
                "name": "S3_METADATA",
                "value": f"address={task_params['address']},address_type={task_params['address_type']}"

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

    def start(self, validate_data=None, queue_input=None):
        # Pass in variables by name for:
        # ValidateData=func() - optional (validates the event data)
        # TaskCode=func() - the code to execute for this task

        if queue_input == None:
            queue_input = self.record_from_queue
        self.event['ssm_params'] = self.get_ssm_params(
            self.ssm_client, [self.PRIVATE_SUBNETS,
                              self.SUBNETS, self.CLUSTER, self.RESULTS, self.SECURITY_GROUP, self.IMAGE_ID])
        self.process_records(self.submit_ecs_task, validate_data, queue_input)
