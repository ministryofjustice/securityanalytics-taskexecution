import pytest
from asyncio import Future, gather
from unittest.mock import MagicMock, call, patch
from test_utils.test_utils import future_of

from asyncio import sleep as real_sleep

with patch("asyncio.sleep") as sleeper:
    from dns_ingestor.ingestor import DnsZoneIngestor
    # Make the sleep take no time at all
    sleeper.return_value = future_of(None)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_zones_present():
        route53_client = MagicMock()
        record_consumer = MagicMock()
        ingestor = DnsZoneIngestor(route53_client)

        route53_client.list_hosted_zones.return_value = future_of({
            "HostedZones": [],
            "IsTruncated": False
        })

        await ingestor.ingest_zones()

        assert ingestor.num_records == 0
        assert ingestor.num_zones == 0
        route53_client.list_hosted_zones.assert_called_once()
        assert record_consumer.call_count == 0

    # This test has a list of zones with 1 page containing 1 zone
    # This zone has a list of records with 1 page containing 1 record
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_simple():
        route53_client = MagicMock()
        record_consumer_mock = MagicMock()

        async def record_consumer(record):
            return record_consumer_mock(record)

        ingestor = DnsZoneIngestor(route53_client)

        route53_client.list_hosted_zones.return_value = future_of({
            "HostedZones": [{
                "Id": "/hostedzone/Z31RX3GZS94JZS",
                "Name": "dsd.io.",
                "ResourceRecordSetCount": 1
            }],
            "IsTruncated": False
        })

        route53_client.list_resource_record_sets.return_value = future_of({
            "ResourceRecordSets": [{
                "Name": "dsd.io.",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z1BKCTXD74EZPE",
                    "DNSName": "s3-website-eu-west-1.amazonaws.com.",
                    "EvaluateTargetHealth": False
                }
            }],
            "IsTruncated": False
        })

        await ingestor.ingest_zones()
        await ingestor.ingest_records(record_consumer)

        assert ingestor.num_records == 1
        assert ingestor.num_zones == 1
        route53_client.list_hosted_zones.assert_called_once()
        record_consumer_mock.assert_called_once_with({
            "Name": "dsd.io.",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z1BKCTXD74EZPE",
                "DNSName": "s3-website-eu-west-1.amazonaws.com.",
                "EvaluateTargetHealth": False
            }
        })

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_paging_zones():
        route53_client = MagicMock()
        record_consumer_mock = MagicMock()

        async def record_consumer(record):
            return record_consumer_mock(record)

        ingestor = DnsZoneIngestor(route53_client)

        route53_client.list_hosted_zones.side_effect = [
            future_of({
                "HostedZones": [{
                    "Id": "/hostedzone/Z31RX3GZS94JZS",
                    "Name": "dsd.io.",
                    "ResourceRecordSetCount": 1
                }],
                "IsTruncated": True,
                "NextMarker": "Sandy"
            }),
            future_of({
                "HostedZones": [{
                    "Id": "/hostedzone/584EWFWE",
                    "Name": "waaaaa.io.",
                    "ResourceRecordSetCount": 1
                }],
                "IsTruncated": True,
                "NextMarker": "Randy"
            }),
            future_of({
                "HostedZones": [{
                    "Id": "/hostedzone/kjonwofweno",
                    "Name": "Nananana.io.",
                    "ResourceRecordSetCount": 1
                }],
                "IsTruncated": False
            })
        ]

        route53_client.list_resource_record_sets.return_value = future_of({
            "ResourceRecordSets": [],
            "IsTruncated": False
        })

        await ingestor.ingest_zones()
        await ingestor.ingest_records(record_consumer)

        assert ingestor.num_records == 0
        assert ingestor.num_zones == 3
        assert route53_client.list_hosted_zones.call_args_list == [
            call(MaxItems="100"),
            call(MaxItems="100", Marker="Sandy"),
            call(MaxItems="100", Marker="Randy")
        ]
        assert record_consumer_mock.call_count == 0

    # N.B. that the next record identifier may or may not be present, so the test tests that is
    # is removed if not present
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_paging_records():
        route53_client = MagicMock()
        record_consumer_mock = MagicMock()

        async def record_consumer(record):
            return record_consumer_mock(record)

        ingestor = DnsZoneIngestor(route53_client)

        route53_client.list_hosted_zones.return_value = future_of({
                "HostedZones": [{
                    "Id": "/hostedzone/Z31RX3GZS94JZS",
                    "Name": "dsd.io.",
                    "ResourceRecordSetCount": 1
                }],
                "IsTruncated": False
            })

        # Three pages, the first has NextRecordIdentifier, second doesn't and third is terminal
        route53_client.list_resource_record_sets.side_effect = [
            future_of({
                "ResourceRecordSets": [
                    {
                        "Name": "a.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "a.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    },
                    {
                        "Name": "b.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "b.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    }
                ],
                "IsTruncated": True,
                "NextRecordName": "Barny",
                "NextRecordType": "Collie",
                "NextRecordIdentifier": "Confucius"
            }),
            future_of({
                "ResourceRecordSets": [
                    {
                        "Name": "c.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "c.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    }
                ],
                "IsTruncated": True,
                "NextRecordName": "Froolio",
                "NextRecordType": "Cantooblek"
            }),
            future_of({
                "ResourceRecordSets": [
                    {
                        "Name": "d.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "d.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    }
                ],
                "IsTruncated": False
            })
        ]

        await ingestor.ingest_zones()
        await ingestor.ingest_records(record_consumer)

        assert ingestor.num_records == 4
        assert ingestor.num_zones == 1
        route53_client.list_hosted_zones.assert_called_once()
        assert route53_client.list_resource_record_sets.call_args_list == [
            call(HostedZoneId="/hostedzone/Z31RX3GZS94JZS", MaxItems="100"),
            call(
                HostedZoneId="/hostedzone/Z31RX3GZS94JZS",
                MaxItems="100",
                StartRecordName="Barny",
                StartRecordType="Collie",
                StartRecordIdentifier="Confucius"
            ),
            call(
                HostedZoneId="/hostedzone/Z31RX3GZS94JZS",
                MaxItems="100",
                StartRecordName="Froolio",
                StartRecordType="Cantooblek")
        ]
        assert record_consumer_mock.call_count == 4

    # N.B. that the next record identifier may or may not be present, so the test tests that is
    # is removed if not present
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sleeps_between_record_pages():
        route53_client = MagicMock()
        record_consumer_mock = MagicMock()

        async def record_consumer(record):
            return record_consumer_mock(record)

        ingestor = DnsZoneIngestor(route53_client)

        route53_client.list_hosted_zones.return_value = future_of({
            "HostedZones": [{
                "Id": "/hostedzone/Z31RX3GZS94JZS",
                "Name": "dsd.io.",
                "ResourceRecordSetCount": 1
            }],
            "IsTruncated": False
        })

        # The two pages give us the opportunity to test the sleep
        route53_client.list_resource_record_sets.side_effect = [
            future_of({
                "ResourceRecordSets": [
                    {
                        "Name": "a.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "a.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    }
                ],
                "IsTruncated": True,
                "NextRecordName": "A",
                "NextRecordType": "B",
                "NextRecordIdentifier": "C"
            }),
            future_of({
                "ResourceRecordSets": [
                    {
                        "Name": "d.dsd.io.",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z1BKCTXD74EZPE",
                            "DNSName": "d.s3-website-eu-west-1.amazonaws.com.",
                            "EvaluateTargetHealth": False
                        }
                    }
                ],
                "IsTruncated": False
            })
        ]

        await ingestor.ingest_zones()

        sleeper.return_value = Future()

        # dispatch but do not await
        ingest_future = gather(ingestor.ingest_records(record_consumer))

        # Bit naff, I would rather have an event loop append task, but this is easier
        await real_sleep(0.1)

        # test that only one call to list_resource_record_sets is made before the sleep is completed
        assert ingestor.num_records == 1
        assert ingestor.num_zones == 1
        route53_client.list_hosted_zones.assert_called_once()
        route53_client.list_resource_record_sets.assert_called_once()
        assert record_consumer_mock.call_count == 1

        # Now resolve the sleep's future and await the completed ingestion process
        sleeper.return_value.set_result(None)
        await ingest_future

        # test that only one call to list_resource_record_sets is made before the sleep is completed
        assert ingestor.num_records == 2
        assert ingestor.num_zones == 1
        assert route53_client.list_resource_record_sets.call_count == 2
        assert record_consumer_mock.call_count == 2
