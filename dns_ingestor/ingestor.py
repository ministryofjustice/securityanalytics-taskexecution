from asyncio import sleep
from itertools import islice


# This class knows how to query route53 and resolve the IPs for all hosts recorded
# TODO this class should probably now be split into two, the zone ingestor and the record ingestor
class DnsZoneIngestor:
    def __init__(self, route53_client, rate_limit_slowdown=0.3):
        self.known_zones = {}
        self.record_count = {}
        self.route53_client = route53_client
        self.num_zones = 0
        self.num_records = 0
        self.ingested_zones = False

    # Call to load the zone info from route 53
    # Handles the pagination querying all zones
    async def ingest_zones(self):
        if self.ingested_zones:
            raise RuntimeError("Shouldn't call ingest_zones twice with same object")

        pagination_params = {"MaxItems": "100"}
        listed_all_zones = False

        # reads zones a page at a time
        while not listed_all_zones:
            zone_page = await self._ingest_page_of_zones(pagination_params)

            # update pagination query params
            listed_all_zones = not bool(zone_page["IsTruncated"])
            if not listed_all_zones:
                pagination_params["Marker"] = zone_page["NextMarker"]

        self.ingested_zones = True

    # records the name and id of all the zones in a single page
    async def _ingest_page_of_zones(self, pagination_params):
        zone_page = await self.route53_client.list_hosted_zones(**pagination_params)
        zones_in_page = zone_page["HostedZones"]

        # update the records that we need to resolve host for this zone
        for zone in zones_in_page:
            zone_id = zone["Id"]
            self.known_zones[zone_id] = zone["Name"]
            self.record_count[zone_id] = 0

        self.num_zones += len(zones_in_page)
        return zone_page

    # Loads all the zones first and then queries each of the zones in turn
    # Rate limit makes it silly to do them in parallel
    async def ingest_records(self, record_consumer):
        if not self.ingested_zones:
            raise RuntimeError("Need to call ingest_zones prior to ingest_records")

        for zone_id, name in self.known_zones.items():
            await self._ingest_records_from_zone(zone_id, name, record_consumer)
        print(f"Finished ingesting from route53 {self.num_records} records found in {self.num_zones} zones")

    # Handles the pagination querying all the records for a given zone
    async def _ingest_records_from_zone(self, zone_id, name, record_consumer):
        pagination_params = {"MaxItems": "100"}
        finished_listing_resources = False

        # reads records a page at a time
        while not finished_listing_resources:
            record_page = await self._ingest_page_of_records(zone_id, record_consumer, pagination_params)

            # Update the pagination params for the next page
            finished_listing_resources = not bool(record_page["IsTruncated"])
            if not finished_listing_resources:
                pagination_params["StartRecordName"] = record_page["NextRecordName"]
                pagination_params["StartRecordType"] = record_page["NextRecordType"]
                if "NextRecordIdentifier" in record_page:
                    pagination_params["StartRecordIdentifier"] = record_page["NextRecordIdentifier"]
                elif "StartRecordIdentifier" in pagination_params:
                    del pagination_params["StartRecordIdentifier"]

        print(f"Ingested zone: {name}, {self.record_count[zone_id]} records")

    async def _ingest_page_of_records(self, zone_id, record_consumer, pagination_params):
        got_set = False
        # We have no control over Route 53, so if we hit the global rate limit then wait 5 seconds and try again
        while not got_set:
            try:
                record_page = await self.route53_client.list_resource_record_sets(HostedZoneId=zone_id, **pagination_params)
                got_set = True
            except:
                print("throttled")
                await sleep(5)

        record_sets = record_page["ResourceRecordSets"]

        # update records processed with length of record set
        records_in_page = len(record_sets)
        self.num_records += records_in_page
        self.record_count[zone_id] += records_in_page

        # the
        for record in record_sets:
            await record_consumer(record)

        # Since route53 api is rate limited to 5 calls a second
        # we add another task to our gather operation so we are not done until it elapsed too
        # Have added a 30% error margin to ensure it will complete
        await sleep(2.5 / 5.0)
        return record_page
