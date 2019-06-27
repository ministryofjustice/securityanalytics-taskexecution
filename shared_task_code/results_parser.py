import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from utils.objectify_dict import objectify
import tarfile
import re
import io
import datetime
from urllib.parse import unquote_plus
import importlib.util
from utils.scan_results import ResultsContext


class ResultsParser:
    region = os.environ["REGION"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    stage = os.environ["STAGE"]
    ssm_prefix = f"/{app_name}/{stage}"
    ssm_client = boto3.client("ssm", region_name=region)
    SNS_TOPIC = f"{ssm_prefix}/tasks/{task_name}/results/arn"
    s3_client = boto3.client("s3", region_name=region)
    sns_client = boto3.client("sns", region_name=region)

    def get_ssm_params(self, ssm_client, *param_names):
        ret = self.ssm_client.get_parameters(Names=[*param_names])
        params = ret['Parameters']
        return {p['Name']: p['Value'] for p in params}

    def __init__(self, event):
        self.event = event

    def post_results(self, topic, doc_type, document):
        r = self.sns_client.publish(
            TopicArn=topic, Subject=doc_type, Message=dumps(document)
        )
        print(f"Published message {r['MessageId']}")

    def process_results(self, topic, bucket, key):
        obj = self.s3_client.get_object(Bucket=bucket, Key=key)

        # extract the message data from the S3 Metadata, and remove the suffix added to the keys by boto3
        metadata = obj["Metadata"]
        msgdata = {'records': []}
        for metakey in metadata:
            # strip out the header that AWS adds
            msgdata[metakey.replace('x-amz-meta-', '')] = metadata[metakey]

        # extract the results from the tar file
        content = obj["Body"].read()
        tar = tarfile.open(mode="r:gz", fileobj=io.BytesIO(content), format=tarfile.PAX_FORMAT)
        result_file_name = re.sub(r"\.tar.gz$", "", key.split("/", -1)[-1])
        body = tar.extractfile(result_file_name).read()

        # there might be times where we want to handle the results ourselves, if so, pass out
        # the file and let the scanning task handle it themselves, otherwise set up ResultsContext
        # and pass the body back to the scanning task

        if self.func_custom_data_handler != None:
            # TODO: document this
            self.func_custom_data_handler(body, tar_data=tar, msg_data=msgdata, task_topic=topic, task_bucket=bucket, task_key=key, result_file_name=result_file_name, sns_client=self.sns_client)
        else:
            start_time, end_time = msgdata["start_time"], msgdata["end_time"]
            scan_id = os.path.splitext(result_file_name)[0]

            # set up the base set of keys to send to elastic
            if "address" in msgdata:
                non_temporal_key = {
                    "address": msgdata['address'],
                    "address_type": msgdata['address_type']
                }
            else:
                non_temporal_key = {}

            results_context = ResultsContext(topic, non_temporal_key, scan_id, start_time,
                                             end_time, self.task_name, self.sns_client)
            if self.func_process_results_file != None:
                self.func_process_results_file(results_context, body, task_topic=topic, task_bucket=bucket, task_key=key)

    def start(self, pre_process_record=None, process_results_file=None, custom_data_handler=None):
        # Pass in variables by name for:
        # PreProcessRecord=func() - optional
        # IterateResults=func() - mandatory
        # CustomDataHandler=func() - optional - if you want to handle the results yourself
        self.event['ssm_params'] = self.get_ssm_params(self.ssm_client, self.SNS_TOPIC)
        topic = self.event['ssm_params'][self.SNS_TOPIC]
        self.func_pre_process_record = pre_process_record
        self.func_process_results_file = process_results_file
        self.func_custom_data_handler = custom_data_handler
        for record in self.event["Records"]:
            s3_object = objectify(record["s3"])
            bucket = s3_object.bucket.name
            key = unquote_plus(s3_object.object.key)
            if self.func_pre_process_record != None:
                (topic, bucket, key) = self.func_pre_process_record(topic, bucket, key)
            self.process_results(topic, bucket, key)
