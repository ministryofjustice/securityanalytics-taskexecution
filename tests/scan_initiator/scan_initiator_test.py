import pytest
import os
import itertools
from unittest.mock import patch, MagicMock, call
from test_utils.test_utils import AsyncContextManagerMock, coroutine_of, resetting_mocks
from boto3.dynamodb.conditions import Key
from decimal import Decimal

TEST_ENV = {
    'REGION': 'eu-west-wood',
    'STAGE': 'door',
    'APP_NAME': 'me-once',
}


@pytest.fixture
def scan_initiator():
    with patch.dict(os.environ, TEST_ENV), \
         patch('aioboto3.client') as boto_client, \
            patch('aioboto3.resource') as boto_resource:
        # ensure each client is a different mock
        boto_client.side_effect = (MagicMock() for _ in itertools.count())
        boto_resource.side_effect = (MagicMock() for _ in itertools.count())
        from scan_initiator import scan_initiator

        yield scan_initiator

        scan_initiator.dynamo_resource.reset_mock()
        scan_initiator.sqs_client.reset_mock()

        scan_initiator.clean_clients()


@patch.dict(os.environ, TEST_ENV)
def set_ssm_return_vals(ssm_client, period, buckets):
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"

    ssm_client.get_parameters.return_value = coroutine_of({
            'Parameters': [
                {"Name": f"{ssm_prefix}/scheduler/dynamodb/id", "Value": "MyTableId"},
                {"Name": f"{ssm_prefix}/scheduler/dynamodb/plan_index", "Value": "MyIndexName"},
                {"Name": f"{ssm_prefix}/scheduler/config/period", "Value": str(period)},
                {"Name": f"{ssm_prefix}/scheduler/config/buckets", "Value": str(buckets)},
                {"Name": f"{ssm_prefix}/scheduler/scan_delay_queue", "Value": "MyDelayQueue"}
            ]
        })


def _mock_delete_responses(mock_plan_table, side_effects):
    mock_batch_writer = AsyncContextManagerMock()
    mock_plan_table.batch_writer.return_value = mock_batch_writer
    mock_batch_writer.aenter.delete_item.side_effect = side_effects
    return mock_batch_writer.aenter


@patch("random.uniform", return_value=9)
@patch("time.time", return_value=1984)
@pytest.mark.unit
def test_paginates_scan_results(uniform, time, scan_initiator):
    # ssm params don't matter much in this test
    set_ssm_return_vals(scan_initiator.ssm_client, 40, 10)

    # access mock for dynamodb table
    scan_initiator.dynamo_resource.Table.return_value = mock_plan_table = MagicMock()

    # return a single result but with a last evaluated key present, second result wont have
    # that key
    mock_plan_table.scan.side_effect = [
        coroutine_of({
            "Items": [{
                "Address": "123.456.123.456",
                "DnsIngestTime": 12345
            }],
            "LastEvaluatedKey": "SomeKey"
        }),
        coroutine_of({
            "Items": [{
                "Address": "456.345.123.123",
                "DnsIngestTime": 123456
            }]
        }),
    ]

    # pretend the sqs messages are all successfully dispatched
    scan_initiator.sqs_client.send_message_batch.side_effect = [
        coroutine_of(None),
        coroutine_of(None)
    ]
    # pretend the delete item calls are all successful too
    writer = _mock_delete_responses(mock_plan_table, [coroutine_of(None), coroutine_of(None)])

    # actually do the test
    scan_initiator.initiate_scans({}, MagicMock())

    # check the scan happens twice
    assert mock_plan_table.scan.call_args_list == [
        call(
            IndexName="MyIndexName",
            FilterExpression=Key("PlannedScanTime").lte(Decimal(1984))
        ),
        call(
            IndexName="MyIndexName",
            FilterExpression=Key("PlannedScanTime").lte(Decimal(1984)),
            ExclusiveStartKey="SomeKey"
        )
    ]

    # Doesn't batch across pages
    assert scan_initiator.sqs_client.send_message_batch.call_count == 2
    assert writer.delete_item.call_count == 2


@patch("random.uniform", return_value=4)
@patch("time.time", return_value=1984)
@pytest.mark.unit
def test_creates_delays_uniformly_for_range(time, uniform, scan_initiator):
    # We have a period of 100 and 4 buckets, so the range should be 0-25
    set_ssm_return_vals(scan_initiator.ssm_client, 100, 4)

    # access mock for dynamodb table
    scan_initiator.dynamo_resource.Table.return_value = mock_plan_table = MagicMock()

    # return a single result
    mock_plan_table.scan.side_effect = [
        coroutine_of({
            "Items": [{
                "Address": "123.456.123.456",
                "DnsIngestTime": 12345
            }]
        })
    ]

    # pretend the sqs and dynamo deletes are all ok
    scan_initiator.sqs_client.send_message_batch.side_effect = [coroutine_of(None)]
    _mock_delete_responses(mock_plan_table, [coroutine_of(None)])

    # actually do the test
    scan_initiator.initiate_scans({}, MagicMock())

    # check that the call to uniform has the correct args and that the supplied mock value is used
    uniform.assert_called_once_with(0, 25)
    scan_initiator.sqs_client.send_message_batch.assert_called_once_with(
        QueueUrl="MyDelayQueue",
        Entries=[{
            "Id": "123-456-123-456",
            "DelaySeconds": 4,
            "MessageBody": "{\"CloudWatchEventHosts\":[\"123.456.123.456\"]}"
        }]
    )


@patch("random.uniform", return_value=4)
@patch("time.time", return_value=1984)
@pytest.mark.unit
def test_replace_punctuation_in_address_ids(uniform, time, scan_initiator):
    # ssm params don't matter much in this test
    set_ssm_return_vals(scan_initiator.ssm_client, 100, 4)

    # access mock for dynamodb table
    scan_initiator.dynamo_resource.Table.return_value = mock_plan_table = MagicMock()

    # return a single result with ip4 and another with ip6
    mock_plan_table.scan.side_effect = [
        coroutine_of({
            "Items": [
                {
                    "Address": "123.456.123.456",
                    "DnsIngestTime": 12345
                },
                {
                    "Address": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                    "DnsIngestTime": 12345
                }
            ]
        })
    ]

    # pretend the sqs and dynamo deletes are all ok
    scan_initiator.sqs_client.send_message_batch.side_effect = [coroutine_of(None)]
    _mock_delete_responses(mock_plan_table, [coroutine_of(None), coroutine_of(None)])

    # actually do the test
    scan_initiator.initiate_scans({}, MagicMock())

    # check both addresses have : and . replaced with -
    scan_initiator.sqs_client.send_message_batch.assert_called_once_with(
        QueueUrl="MyDelayQueue",
        Entries=[
            {
                "Id": "123-456-123-456",
                "DelaySeconds": 4,
                "MessageBody": "{\"CloudWatchEventHosts\":[\"123.456.123.456\"]}"
            },
            {
                "Id": "2001-0db8-85a3-0000-0000-8a2e-0370-7334",
                "DelaySeconds": 4,
                "MessageBody": "{\"CloudWatchEventHosts\":[\"2001:0db8:85a3:0000:0000:8a2e:0370:7334\"]}"
            }
        ]
    )


@patch("random.uniform", return_value=4)
@patch("time.time", return_value=1984)
@pytest.mark.unit
def test_batches_sqs_writes(uniform, time, scan_initiator):
    # ssm params don't matter much in this test
    set_ssm_return_vals(scan_initiator.ssm_client, 100, 4)

    # access mock for dynamodb table
    scan_initiator.dynamo_resource.Table.return_value = mock_plan_table = MagicMock()

    # send 32 responses in a single scan result, will be batched into groups of 10 for
    # sqs
    mock_plan_table.scan.side_effect = [
        coroutine_of({
            "Items": [
                {
                    "Address": f"123.456.123.{item_num}",
                    "DnsIngestTime": 12345
                }
                for item_num in range(0, 32)
            ]
        })
    ]

    # pretend the sqs and dynamo deletes are all ok, there are 4 calls to sqs
    # and
    scan_initiator.sqs_client.send_message_batch.side_effect = [
        coroutine_of(None) for _ in range(0, 4)
    ]
    writer = _mock_delete_responses(mock_plan_table, [
        coroutine_of(None) for _ in range(0, 32)
    ])

    # actually do the test
    scan_initiator.initiate_scans({}, MagicMock())

    # There will be 4 calls to  sqs
    assert scan_initiator.sqs_client.send_message_batch.call_count == 4

    # The last batch will have 2 remaining items in it N.B. a call object is a tuple of the
    # positional args and then the kwags
    assert len(scan_initiator.sqs_client.send_message_batch.call_args_list[3][1]["Entries"]) == 2

    # There will be individual deletes for each address i.e. 32 of them
    assert writer.delete_item.call_count == 32


@patch("random.uniform", return_value=4)
@patch("time.time", return_value=1984)
@pytest.mark.unit
def test_no_deletes_until_all_sqs_success(uniform, time, scan_initiator):
    # ssm params don't matter much in this test
    set_ssm_return_vals(scan_initiator.ssm_client, 100, 4)

    # access mock for dynamodb table
    scan_initiator.dynamo_resource.Table.return_value = mock_plan_table = MagicMock()

    # send a single response
    mock_plan_table.scan.side_effect = [
        coroutine_of({
            "Items": [
                {
                    "Address": f"123.456.123.5",
                    "DnsIngestTime": 12345
                }
            ]
        })
    ]

    # pretend the sqs and dynamo deletes are all ok, there are 4 calls to sqs
    # and
    scan_initiator.sqs_client.send_message_batch.side_effect = [
        Exception("test error")
    ]
    writer = _mock_delete_responses(mock_plan_table, [])

    # actually do the test
    with pytest.raises(Exception):
        scan_initiator.initiate_scans({}, MagicMock())

    # There will be 1 call to sqs
    assert scan_initiator.sqs_client.send_message_batch.call_count == 1

    # and none to dynamo
    assert writer.delete_item.call_count == 0



