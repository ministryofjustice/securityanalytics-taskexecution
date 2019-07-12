from abc import abstractmethod
from .scanning_lambda import ScanningLambda
from asyncio import gather


class BaseScanner(ScanningLambda):
    def __init__(self):
        super().__init__()

    # Implementing this method implements a scan
    @abstractmethod
    async def scan(self, scan_request_id, scan_request):
        pass

    async def invoke_impl(self, event, context):
        print(event)
        await super().invoke_impl(event, context)
        await gather(*[
            self._logging_scan(record["messageId"], record["body"])
            for record in event["Records"]
        ])

    async def _logging_scan(self, scan_request_id, scan_request):
        print(f"Scanning request {scan_request_id} {scan_request}")
        return await self.scan(scan_request_id,scan_request)
