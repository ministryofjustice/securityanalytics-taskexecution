from abc import ABC, abstractmethod
from .scanning_lambda import ScanningLambda
from lambda_templates.sqs_consumer_mixin import SqsConsumerMixin


class BaseScanner(ABC, ScanningLambda, SqsConsumerMixin):
    def __init__(self, ssm_params_to_load):
        ScanningLambda.__init__(self, ssm_params_to_load)

    # Implementing this method implements a scan
    @abstractmethod
    async def _scan(self, scan_request_id, scan_request):
        pass

    # Overriding this method allows subclasses to initialise clients
    @abstractmethod
    async def _initialise(self):
        pass

    # Doesn't do anything here, but it is a useful extension point for other subclasses
    async def _process_event(self, scan_request_id, scan_request):
        return await self._scan(scan_request_id, scan_request)

