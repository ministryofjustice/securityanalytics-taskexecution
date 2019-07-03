import os
import aioboto3
from utils.lambda_decorators import ssm_parameters, async_handler
from abc import ABC, abstractmethod


class BaseScanner(ABC):
    def __init__(self, ssm_params_to_load):
        ABC.__init__(self)
        self.region = os.environ["REGION"]
        self.stage = os.environ["STAGE"]
        self.app_name = os.environ["APP_NAME"]
        self.task_name = os.environ["TASK_NAME"]
        self._ssm_prefix = f"/{self.app_name}/{self.stage}"
        self._ssm_params_to_load = [f"${self.ssm_prefix}/${x}" for x in ssm_params_to_load]

        # Make sure we always request the results bucket param
        self._results_bucket_param = f"{self.ssm_prefix}/tasks/{self.task_name}/s3/results/id"
        if self.results_bucket_param not in self._ssm_params_to_load:
            self._ssm_params_to_load.append(self.results_bucket_param)

        self.event = None
        self.context = None
        self.initialised = False
        self.ssm_client = None
        self.ssm_params = None

    # Implementing this method implements a scan
    @abstractmethod
    async def _scan(self, scan_request_id, scan_request):
        pass

    # Overriding this method allows subsclasses to initialise clients
    @abstractmethod
    async def _initialise(self):
        pass

    # The scans can get access to the s3 bucket using this method
    def results_bucket(self):
        return self.event.ssm_params[self._results_bucket_param]

    # Other ssm params can be accessed with this method, uses relative name e.g.
    # use "/lambda/layers/utils/arn", instead of "/sec-an/dev/lambda/layers/utils/arn"
    def get_ssm_param(self, relative_name):
        if not relative_name.starts_with("/"):
            relative_name = f"/{relative_name}"
        return self.event.ssm_params[f"{self._ssm_prefix}{relative_name}"]

    @async_handler
    async def handle_event(self, event, context):
        self.context = context
        self.event = event
        await self._ensure_initialised()

        @ssm_parameters(self.ssm_params, self._ssm_params_to_load)
        async def perform_scan_wth_params(_event, _context):
            for record in self.event["Records"]:
                scan_request = record["body"]
                scan_request_id = record["messageId"]

                await self._invoke_scan_impl(scan_request_id, scan_request)

    # Doesn't do anything here, but it is a useful extension point for other subclasses
    async def _invoke_scan_impl(self, scan_request_id, scan_request):
        return await self._scan(scan_request_id, scan_request)

    async def _ensure_initialised(self):
        if not self.initialised:
            self.initialised = True
            self.ssm_client = aioboto3.client("ssm", region_name=self.region)
            # call the subclasses' initialisers
            await self._initialise()
