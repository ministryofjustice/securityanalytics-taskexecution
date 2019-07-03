from abc import ABC, abstractmethod
from .scanning_lambda import ScanningLambda
from utils.objectify_dict import objectify
from urllib.parse import unquote_plus
import aioboto3
import tarfile
import re
import io
from asyncio import gather


class ResultsParser(ABC, ScanningLambda):
    def __init__(self, ssm_params_to_load):
        ScanningLambda.__init__(self, ssm_params_to_load)

    async def _initialise(self):
        self.ecs_client = aioboto3.client("ecs", region_name=self.region)

    @abstractmethod
    async def _parse_results(self, results_doc, meta_data):
        pass

    # Process all the results, N.B. assumes processing of each record is independent
    async def _invoke(self, event, _):
        return await gather(*[self._load_results(record) for record in event["Records"]])

    async def _load_results(self, record):
        s3_object = objectify(record["s3"])
        key = unquote_plus(s3_object.object.key)
        obj = await self.s3_client.get_object(Bucket=self.results_bucket(), Key=key)
        # extract the message data from the S3 Metadata,
        # and remove the suffix added to the keys by boto3
        meta_data = self._extract_meta_data(obj)
        # extract the results from the tar file
        content = obj["Body"].read()
        tar = tarfile.open(mode="r:gz", fileobj=io.BytesIO(content), format=tarfile.PAX_FORMAT)
        result_file_name = re.sub(r"\.tar.gz$", "", key.split("/", -1)[-1])
        results_doc = tar.extractfile(result_file_name).read()
        await self._parse_results(results_doc, meta_data)

    @staticmethod
    def _extract_meta_data(obj):
        metadata = obj["Metadata"]
        msgdata = {'records': []}
        for metakey in metadata:
            # strip out the header that AWS adds
            msgdata[metakey.replace('x-amz-meta-', '')] = metadata[metakey]
        return msgdata




