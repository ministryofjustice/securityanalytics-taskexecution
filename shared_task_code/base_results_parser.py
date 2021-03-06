from abc import abstractmethod
from .scanning_lambda import ScanningLambda
from utils.objectify_dict import objectify
from urllib.parse import unquote_plus
import aioboto3
import tarfile
import re
import io
from asyncio import gather
from utils.scan_results import ResultsContext


class ResultsParser(ScanningLambda):
    def __init__(self):
        super().__init__()
        self.sns_client = None

        # Add the SNS topic to the params to retrieve
        self._sns_topic_param = f"{self.ssm_stage_prefix}/tasks/{self.task_name}/results/arn"

    def ssm_parameters_to_load(self):
        return super().ssm_parameters_to_load() + [self._sns_topic_param]

    def initialise(self):
        super().initialise()
        self.sns_client = aioboto3.client("sns", region_name=self.region)

    @abstractmethod
    async def parse_results(self, results_file_name, results_doc, meta_data):
        pass

    def create_results_context(self, non_temporal_key, scan_id, start_time, end_time):
        return ResultsContext(
            self.get_ssm_param(self._sns_topic_param),
            non_temporal_key,
            scan_id,
            start_time,
            end_time,
            self.task_name,
            self.sns_client
        )

    # Process all the results, N.B. assumes processing of each record is independent.
    async def invoke_impl(self, event, context):
        await super().invoke_impl(event, context)
        return await gather(*[self._load_results(record) for record in event["Records"]])

    async def _load_results(self, record):
        s3_object = objectify(record["s3"])
        key = unquote_plus(s3_object.object.key)
        bucket = self.results_bucket()
        print(f"Reading new file: {(bucket, key)}")
        obj = await self.s3_client.get_object(Bucket=bucket, Key=key)

        # extract the message data from the S3 Metadata,
        # and remove the suffix added to the keys by boto3
        meta_data = self._extract_meta_data(obj)
        # extract the results from the tar file
        content = await obj["Body"].read()

        tar = tarfile.open(mode="r:gz", fileobj=(io.BytesIO(content)), format=tarfile.PAX_FORMAT)
        result_file_name = re.sub(r"\.tar.gz$", "", key.split("/", -1)[-1])
        results_doc = tar.extractfile(result_file_name)

        await self.parse_results(result_file_name, results_doc, meta_data)

    @staticmethod
    def _extract_meta_data(obj):
        metadata = obj["Metadata"] if "Metadata" in obj else {}
        msgdata = {'records': []}
        for metakey in metadata:
            # strip out the prefix that AWS adds
            msgdata[metakey.replace('x-amz-meta-', '')] = metadata[metakey]
        return msgdata




