import aioboto3
from utils.json_serialisation import dumps
from abc import abstractmethod
from .base_scanner import BaseScanner
import os


class EcsScanner(BaseScanner):

    def __init__(self, ssm_params_to_load):
        self.ecs_client = None

        self._private_subnets_param = "/vpc/using_private_subnets"
        self._subnets_param = "/vpc/subnets/instance"
        self._cluster_param = "/ecs/cluster"
        task_name = os.environ["TASK_NAME"]
        self._security_group_param = f"/tasks/{task_name}/security_group/id"
        self._image_id_param = f"/tasks/{task_name}/image/id"

        ssm_params_to_load += [
            self._private_subnets_param,
            self._subnets_param,
            self._cluster_param,
            self._security_group_param,
            self._image_id_param
        ]
        super().__init__(ssm_params_to_load)

    def initialise(self):
        self.ecs_client = aioboto3.client("ecs", region_name=self.region)

    # This method is implemented by subclasses of the EcsScanStarter to extract environment variables
    # from the event received. Should return a dictionary.
    @abstractmethod
    async def create_environment_from_request(self, scan_request_id, scan_request):
        pass

    async def scan(self, scan_request_id, scan_request):
        await super().scan(scan_request_id, scan_request)
        print(f"Scanning {scan_request_id} - {scan_request}")
        task_environment = await self.create_environment_from_request(scan_request_id, scan_request)

        private_subnet = "true" == self.get_ssm_param(self._private_subnets_param)
        network_configuration = {
            "awsvpcConfiguration": {
                "subnets": self.get_ssm_param(self._subnets_param).split(","),
                "securityGroups": [self.get_ssm_param(self._security_group_param)],
                "assignPublicIp": "DISABLED" if private_subnet else "ENABLED"
            }
        }
        env_obj = [
            # Add the env vars the subclass determined we need
            *[
                {
                    "name": key,
                    "value": value
                }
                for key, value in task_environment.items()
            ],
            # Then add the ones we absolutely need, always
            {
                "name": "SCAN_REQUEST_ID",
                "value": scan_request_id
            },
            {
                "name": "RESULTS_BUCKET",
                "value": self.results_bucket()
            }]

        ecs_params = {
            "cluster": self.get_ssm_param(self._cluster_param),
            "networkConfiguration": network_configuration,
            "taskDefinition": self.get_ssm_param(self._image_id_param),
            "launchType": "FARGATE",
            "overrides": {
                "containerOverrides": [{
                    "name": self.task_name,
                    "environment": env_obj
                }]
            }
        }
        print(f"Submitting task: {dumps(ecs_params)}")
        task_response = await self.ecs_client.run_task(**ecs_params)
        print(f"Submitted scanning task: {dumps(task_response)}")

        failures = task_response["failures"]
        if len(failures) != 0:
            raise RuntimeError(
                f"ECS task failed to start {dumps(failures)}")
