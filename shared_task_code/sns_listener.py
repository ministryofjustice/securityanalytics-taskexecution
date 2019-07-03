import os
from utils.json_serialisation import dumps
from lambda_templates.lazy_initialising_lambda import LazyInitLambda
from abc import ABC, abstractmethod


class FilteringAndTransformingSnsToSqsGlue(ABC, LazyInitLambda):
    def __init__(self, ssm_params_to_load):
        glue_name = os.environ["GLUE_NAME"]
        self._sqs_targets_param = f"/glue/{glue_name}/targets"
        if self._sqs_targets_param not in ssm_params_to_load:
            ssm_params_to_load.append(self._sqs_targets_param)
        self.sqs_targets = None

        LazyInitLambda.__init__(self, ssm_params_to_load)

    async def initialise(self):
        await LazyInitLambda.initialise(self)
        self.sqs_targets = list(self.get_ssm_param(self._sqs_targets_param))

    async def forward_message(self, json_data, msg_attributes=None):
        print(json_data)
        for sqs_target in self.sqs_targets:
            return await self.sqs_client.send_message(
                QueueUrl=sqs_target,
                MessageBody=dumps(json_data),
                MessageAttributes=msg_attributes
            )

    @abstractmethod
    async def handle_incoming_sns_event(self, sns_message):
        pass

    def _invoke(self, event, context):
        for record in event["Records"]:
            print(record)
            await self.handle_incoming_sns_event(record["Sns"])
