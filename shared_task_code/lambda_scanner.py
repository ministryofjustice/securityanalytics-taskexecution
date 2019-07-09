from .base_scanner import BaseScanner
from datetime import datetime
from utils.time_utils import iso_date_string_from_timestamp
import tarfile
import io
from abc import abstractmethod


class LambdaScanner(BaseScanner):
    def __init__(self, ssm_params_to_load):
        super().__init__(ssm_params_to_load)

    # Overrides the base scan to also handle the results publication for you
    async def process_event(self, scan_request_id, scan_request):
        await super().process_event(scan_request_id, scan_request)
        # Use this format to have uniformly named files in S3
        scan_start_time = iso_date_string_from_timestamp(datetime.now().timestamp())

        # call super
        results, extension, result_meta = await self.scan(scan_request_id, scan_request)
        if results:
            scan_end_time = iso_date_string_from_timestamp(datetime.now().timestamp())
            await self.write_file(
                scan_request_id,
                results,
                extension,
                result_meta,
                scan_start_time,
                scan_end_time
            )

    async def write_file(self, scan_request_id, results, extension, result_meta, scan_start_time, scan_end_time):

        # Add in standard fields
        result_meta["scan_start_time"] = scan_start_time
        result_meta["scan_end_time"] = scan_end_time
        result_meta["TemporalKey"] = scan_end_time
        result_meta["scan_id"] = scan_request_id

        # results file name
        results_filename = f"{scan_request_id}-{scan_start_time}-{self.task_name}.{extension}"

        # create archive
        results_archive_bytes = io.BytesIO()
        with tarfile.open(mode="w:gz", fileobj=results_archive_bytes, format=tarfile.PAX_FORMAT) as tar:
            t = tarfile.TarInfo(results_filename)
            t.size = results.getbuffer().nbytes
            tar.addfile(t, results)
        results_archive_bytes.seek(0)
        # do the upload
        print(result_meta)
        for key in result_meta:
            if not result_meta[key]:
                result_meta[key] = ""
        await self.s3_client.upload_fileobj(
            results_archive_bytes,
            self.results_bucket(),
            f"{results_filename}.tar.gz",
            ExtraArgs={"Metadata": result_meta}
        )

    # Implementing this method implements a lambda scan, it should return a triple:
    # - json object to be serialised with timestamps as the data
    # - file extension for the results file
    # - a dictionary used to setup meta-data
    @abstractmethod
    def scan(self, scan_request_id, scan_request):
        pass  # e.g. return ({"body":"text"},{"meta_key":"meta_value"})
