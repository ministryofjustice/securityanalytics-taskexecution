from .base_scanner import BaseScanner
from datetime import datetime
from utils.time_utils import iso_date_string_from_timestamp
import tarfile
import io
from abc import abstractmethod, ABC


class LambdaScanner(BaseScanner):
    def __init__(self, ssm_params_to_load):
        super().__init__(ssm_params_to_load)

    # Overrides the base scan to also handle the results publication for you
    async def process_event(self, scan_request_id, scan_request):
        await super().process_event(scan_request_id, scan_request)
        # Use this format to have uniformly named files in S3
        scan_start_time = iso_date_string_from_timestamp(datetime.now())
        
        # call super
        results, result_meta = await self.scan(scan_request_id, scan_request)

        scan_end_time = iso_date_string_from_timestamp(datetime.now())

        # Add in standard fields
        result_meta["scan_start_time"] = scan_start_time
        result_meta["scan_end_time"] = scan_end_time
        result_meta["TemporalKey"] = scan_end_time

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
    def scan(self, scan_request_id, scan_request):
        pass  # e.g. return ({"body":"text"},{"meta_key":"meta_value"})
