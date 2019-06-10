import pytest
from asyncio import Future, gather
from unittest.mock import MagicMock
from dns_ingestor.scan_plan_writer import PlannedScanDbWriter
from dns_ingestor.host_to_scan import HostToScan
from test_utils.test_utils import future_of


def mock_table():
    table = MagicMock()
    table.update_item.return_value = future_of(None)
    return table


@pytest.mark.unit
@pytest.mark.asyncio
async def test_uses_schedule():
    schedule = mock_table()
    scan_plan_table = mock_table()
    host_table = mock_table()
    address_table = mock_table()
    address_info_table = mock_table()
    writer = PlannedScanDbWriter(scan_plan_table, host_table, address_table, address_info_table, 999, schedule)
    # asyncly call write 10 times
    await gather(*[
        writer.write(HostToScan("123.4.5.6", "foo.bar")) for _ in range(0, 10)
    ])
    assert schedule.__next__.call_count == 10


@pytest.mark.unit
@pytest.mark.asyncio
async def test_is_async():
    schedule = mock_table()
    scan_plan_table = mock_table()
    host_table = mock_table()
    address_table = mock_table()
    address_info_table = mock_table()
    writer = PlannedScanDbWriter(scan_plan_table, host_table, address_table, address_info_table, 999, schedule)
    # asyncly call write 10 times
    all_writes = gather(*[
        writer.write(HostToScan("123.4.5.6", "foo.bar")) for _ in range(0, 10)
    ])
    assert not all_writes.done()

    # asyncly set the results
    await all_writes

    # check that we now have the calls made
    assert scan_plan_table.update_item.call_count == 10


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dynamo_db_call_params():
    schedule = MagicMock()
    schedule.__next__.return_value = 1050
    scan_plan_table = mock_table()
    host_table = mock_table()
    address_table = mock_table()
    address_info_table = mock_table()
    writer = PlannedScanDbWriter(scan_plan_table, host_table, address_table, address_info_table, 999, schedule)
    await writer.write(HostToScan("123.4.5.6", "foo.bar"))

    scan_plan_table.update_item.assert_called_once_with(
        Key={"Address": "123.4.5.6"},
        UpdateExpression="SET #Hosts = list_append(if_not_exists(#Hosts, :empty_list), :Host), "
                         "PlannedScanTime = if_not_exists(#PlannedScanTime, :PlannedScanTime), "
                         "DnsIngestTime = :DnsIngestTime",
        ExpressionAttributeNames={
            "#Hosts": "HostsResolvingToAddress",
            "#PlannedScanTime": "PlannedScanTime"
        },
        ExpressionAttributeValues={
            ":Host": ["foo.bar"],
            ":PlannedScanTime": 1050,
            ":empty_list": [],
            ":DnsIngestTime": 999
        }
    )

# TODO Add tests for the other 4 tables that are now written to
