from abc import abstractmethod
from .scanning_lambda import ScanningLambda
from asyncio import gather


class BaseScanner(ScanningLambda):
    def __init__(self, ssm_params_to_load):
        super().__init__(ssm_params_to_load)

    # Implementing this method implements a scan
    @abstractmethod
    async def scan(self, scan_request_id, scan_request):
        pass

    async def invoke_impl(self, event, context):
        print(event)
        await super().invoke_impl(event, context)
        await gather(*[
            self.process_event(record["messageId"], record["body"])
            for record in event["Records"]
        ])

    # Doesn't do anything here, but it is a useful extension point for other subclasses
    async def process_event(self, scan_request_id, scan_request):
        return await self.scan(scan_request_id, scan_request)
