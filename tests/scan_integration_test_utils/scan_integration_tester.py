import aioboto3
import os
from .scan_result_capture import ScanResultCapture
from asyncio import gather, sleep
from abc import ABC, abstractmethod
from concurrent.futures import CancelledError


class ScanIntegrationTester(ABC):
    def __init__(self, timeout_seconds=120):
        self.ssm_params = None
        self.ssm_client = None
        self.sqs_client = None
        self.sns_client = None
        self.sqs_input_queue_url = None
        self.sns_output_notifier_arn = None
        self.gathering_coro = None
        self.region = os.environ["REGION"]
        self.stage = os.environ["STAGE"]
        self.app_name = os.environ["APP_NAME"]
        self.task_name = os.environ["TASK_NAME"]
        self.ssm_source_stage = \
            os.environ["SSM_SOURCE_STAGE"] if "SSM_SOURCE_STAGE" in os.environ else self.stage
        self.ssm_stage_prefix = f"/{self.app_name}/{self.stage}"
        self.ssm_source_stage_prefix = f"/{self.app_name}/{self.ssm_source_stage}"

        self.sqs_input_queue = f"{self.ssm_stage_prefix}/tasks/{self.task_name}/task_queue/url"
        self.sns_output_notifier = f"{self.ssm_stage_prefix}/tasks/{self.task_name}/results/arn"

        self.timeout = timeout_seconds
        self.incomplete = True

    async def __aenter__(self):
        self.ssm_client = aioboto3.client("ssm", region_name=self.region)
        self.sqs_client = aioboto3.client("sqs", region_name=self.region)
        self.sns_client = aioboto3.client("sns", region_name=self.region)

        params = await self.ssm_client.get_parameters(Names=[
            *self.ssm_parameters_to_load()
        ])
        self.ssm_params = {p["Name"]: p["Value"] for p in params["Parameters"]}

        self.sqs_input_queue_url = self.ssm_params[self.sqs_input_queue]
        self.sns_output_notifier_arn = self.ssm_params[self.sns_output_notifier]

        print(f"Testing scan from queue {self.sqs_input_queue_url} to topic {self.sns_output_notifier_arn}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await gather(
            self.ssm_client.close(),
            self.sns_client.close(),
            self.sqs_client.close()
        )

    def ssm_parameters_to_load(self):
        return [
            self.sqs_input_queue,
            self.sns_output_notifier
        ]

    def get_ssm_param(self, full_name):
        return self.ssm_params[full_name]

    @abstractmethod
    async def send_request(self):
        pass

    @abstractmethod
    async def handle_results(self, body):
        pass

    async def run_test(self):
        async with self, ScanResultCapture(
                self.sqs_client,
                self.sns_client,
                self.sns_output_notifier_arn,
                self.task_name
        ) as queue_context:
            self.gathering_coro = gather(
                self.poll_responses(queue_context.queue_url),
                self.failure_timeout(),
                self.send_request()
            )
            try:
                await self.gathering_coro
            except CancelledError:
                print("Test was terminated")

    async def poll_responses(self, queue_url):
        while self.incomplete:
            print("Polling...", flush=True)
            poll_resp = await self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=20,
                WaitTimeSeconds=10
            )
            if "Messages" in poll_resp:
                message = poll_resp["Messages"][0]
                receipt_handle = message["ReceiptHandle"]

                # Delete received message from queue
                await self.sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )

                await self.handle_results(message["Body"])

    async def cancel_polling(self):
        print("Cancelling results polling...", flush=True)
        self.incomplete = False
        self.gathering_coro.cancel()

    async def failure_timeout(self):
        await sleep(self.timeout)
        await self.cancel_polling()
        raise AssertionError("Testcase timed out")
