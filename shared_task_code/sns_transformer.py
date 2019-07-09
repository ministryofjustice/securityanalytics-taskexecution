import os
from utils.json_serialisation import dumps
from lambda_templates.lazy_initialising_lambda import LazyInitLambda
from abc import abstractmethod
import aioboto3
from asyncio import gather


class FilteringAndTransformingSnsToSnsGlue(LazyInitLambda):
    def __init__(self, ssm_params_to_load):
        glue_name = os.environ["GLUE_NAME"]
        self._sns_target_topic = f"/glue/{glue_name}/sns_target"
        if self._sns_target_topic not in ssm_params_to_load:
            ssm_params_to_load.append(self._sns_target_topic)
        self.sqs_targets = None
        self.sns_client = None

        super().__init__(ssm_params_to_load)

    def initialise(self):
        super().initialise()
        self.sns_client = aioboto3.client("sns", region_name=self.region)

    async def forward_message(self, json_data, msg_attributes=None):
        print(json_data)
        sns_attributes = {}
        for attr in msg_attributes:
            if msg_attributes[attr] and msg_attributes[attr] != "":
                sns_attributes[attr] = {"DataType": "String", "StringValue": msg_attributes[attr]}
        print(sns_attributes)
        return await self.sns_client.publish(
            TopicArn=self.get_ssm_param(self._sns_target_topic, use_source_stage=True),
            Subject="ports-detected",
            Message=dumps(json_data),
            MessageAttributes=sns_attributes
        )

    @abstractmethod
    async def handle_incoming_sns_event(self, sns_message):
        pass

    async def invoke_impl(self, event, context):
        await super().invoke_impl(event, context)
        await gather(*[
            self.handle_incoming_sns_event(record["Sns"])
            for record in event["Records"]
        ])
