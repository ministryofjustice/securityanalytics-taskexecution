from lambda_templates.lazy_initialising_lambda import LazyInitLambda
from abc import abstractmethod, ABC
import aioboto3
import os


# Adds access to the results bucket and the task name ssm param
class ScanningLambda(ABC, LazyInitLambda):
    def __init__(self, ssm_params_to_load):
        self.task_name = os.environ["TASK_NAME"]

        # Make sure we always request the results bucket param
        self._results_bucket_param = f"{self.ssm_prefix}/tasks/{self.task_name}/s3/results/id"
        if self.results_bucket_param not in self._ssm_params_to_load:
            self._ssm_params_to_load.append(self.results_bucket_param)

        LazyInitLambda.__init__(self, ssm_params_to_load)

    # The scans can get access to the s3 bucket using this method
    def results_bucket(self):
        return self.event.ssm_params[self._results_bucket_param]

    async def _initialise(self):
        self.s3_client = aioboto3.resource("s3", region_name=self.region)

    @abstractmethod
    async def _invoke(self, event, context):
        pass

