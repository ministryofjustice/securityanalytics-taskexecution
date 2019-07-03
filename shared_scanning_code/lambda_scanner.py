from .base_scanner import BaseScanner
from datetime import datetime
from utils.time_utils import iso_date_string_from_timestamp
import tarfile
import io
import aioboto3
from abc import abstractmethod


class LambdaScanner(BaseScanner):
    # Subsclassess overriding this must remember to call it (super) too
    async def _initialise(self):
        self.s3_client = aioboto3.resource("s3", region_name=self.region)

    # Overrides the base scan to also handle the results publication for you
    async def _invoke_scan_impl(self, scan_request_id, scan_request):
        # Use this format to have uniformly named files in S3
        scan_start_time = iso_date_string_from_timestamp(datetime.now())
        
        # call super
        results, result_meta = BaseScanner._invoke_scan_impl(self, scan_request_id, scan_request)

        scan_end_time = iso_date_string_from_timestamp(datetime.now())

        # Add in standard fields
        results["scan_start_time"] = scan_start_time
        results["scan_end_time"] = scan_end_time
        results["TemporalKey"] = scan_end_time

        # results file name
        results_filename = f"{scan_request_id}-{scan_start_time}-{self.task_name}.json"

        # create archive
        results_archive_bytes = io.BytesIO()
        with tarfile.open(mode="w:gz", fileobj=results_archive_bytes, format=tarfile.PAX_FORMAT) as tar:
            tar.add(tarfile.TarInfo(results_filename), io.BytesIO(results))
        results_archive_bytes.seek(0)

        # do the upload
        await self.s3_client.upload_file(
            f"/tmp/{results_filename}.tar.gz",
            self.results_bucket(),
            results_archive_bytes,
            MetaData=result_meta
        )

    # Implementing this method implements a lambda scan, it should return a pair json objects, one to be serialised
    # with timestamps as the data, and the other a dictionary used to setup meta-data
    @abstractmethod
    def _scan(self, scan_request):
        pass
