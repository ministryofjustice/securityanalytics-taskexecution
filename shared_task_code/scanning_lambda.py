from lambda_templates.lazy_initialising_lambda import LazyInitLambda
from abc import abstractmethod
import aioboto3
import os


# Adds access to the results bucket and the task name ssm param
class ScanningLambda(LazyInitLambda):
    def __init__(self):
        super().__init__()
        self.task_name = os.environ["TASK_NAME"]
        self.s3_client = None

        # Make sure we always request the results bucket param
        self.results_bucket_param = f"{self.ssm_stage_prefix}/tasks/{self.task_name}/s3/results/id"

    def ssm_parameters_to_load(self):
        return super().ssm_parameters_to_load() + [
            self.results_bucket_param
        ]

    # The scans can get access to the s3 bucket using this method
    def results_bucket(self):
        return self.get_ssm_param(self.results_bucket_param)

    def initialise(self):
        super().initialise()
        self.s3_client = aioboto3.client("s3", region_name=self.region)

    @abstractmethod
    async def invoke_impl(self, event, context):
        pass

