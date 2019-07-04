import os
from utils.json_serialisation import dumps
from lambda_templates.lazy_initialising_lambda import LazyInitLambda
from abc import ABC, abstractmethod
import aioboto3


class FilteringAndTransformingSnsToSnsGlue(ABC, LazyInitLambda):
    def __init__(self, ssm_params_to_load):
        glue_name = os.environ["GLUE_NAME"]
        self._sns_target_topic = f"/glue/{glue_name}/sns_target"
        if self._sns_target_topic not in ssm_params_to_load:
            ssm_params_to_load.append(self._sns_target_topic)
        self.sqs_targets = None
        self.sns_client = None

        LazyInitLambda.__init__(self, ssm_params_to_load)

    async def initialise(self):
        await LazyInitLambda.initialise(self)
        self.sns_client = aioboto3.client("sns", region_name=self.region)

    async def forward_message(self, json_data, msg_attributes=None):
        print(json_data)
        return await self.sns_client.send_message(
            TopicArn=self.get_ssm_param(self._sns_target_topic),
            Subject="ports-detected",
            Message=dumps(json_data),
            MessageAttributes=msg_attributes
        )

    @abstractmethod
    async def handle_incoming_sns_event(self, sns_message):
        pass

    def _invoke(self, event, context):
        for record in event["Records"]:
            print(record)
            await self.handle_incoming_sns_event(record["Sns"])
