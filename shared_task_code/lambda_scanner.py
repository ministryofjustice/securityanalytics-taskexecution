from .base_scanner import BaseScanner
import tarfile
import io
from abc import abstractmethod


class LambdaScanner(BaseScanner):
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def scan(self, scan_request_id, scan_request):
        pass

    async def write_results_set(
        self,
        scan_request_id,
        results,
        extension,
        result_meta,
        scan_start_time,
        scan_end_time
    ):
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
