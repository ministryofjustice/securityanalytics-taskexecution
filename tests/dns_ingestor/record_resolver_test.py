import pytest
from dns_ingestor.host_to_scan import HostToScan
from dns_ingestor.record_resolver import RecordResolver


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ip4_a_record():
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "A",
            "ResourceRecords": [
                {
                    "Value": "123.321.123.1"
                },
                {
                    "Value": "123.321.123.2"
                }
            ]
        }
    )
    assert results == [
        HostToScan("123.321.123.1", "a.dsd.io."),
        HostToScan("123.321.123.2", "a.dsd.io.")
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ip6_a_record():
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "b.dsd.io.",
            "Type": "AAAA",
            "ResourceRecords": [
                {
                    "Value": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
                },
                {
                    "Value": "9999:0db8:85a3:0000:0000:8a2e:0370:7334"
                }
            ]
        }
    )
    assert results == [
        HostToScan("2001:0db8:85a3:0000:0000:8a2e:0370:7334", "b.dsd.io."),
        HostToScan("9999:0db8:85a3:0000:0000:8a2e:0370:7334", "b.dsd.io.")
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alias_a_record_hosted_zone():
    # Since we have the Z1BKCTXD74EZPE key in the list of no zones, we dont resolve
    # the alias, we will be resolving and scanning it when we read its zone
    results = await RecordResolver({"Z1BKCTXD74EZPE": "a.dsd.io."}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z1BKCTXD74EZPE",
                "DNSName": "a.s3-website-eu-west-1.amazonaws.com.",
                "EvaluateTargetHealth": False
            }
        }
    )
    assert results == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alias_a_record_cant_resolve():
    # The alias name is an invalid host and so should never resolve
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z1BKCTXD74EZPE",
                "DNSName": "ijuwwi w902352 invalid name",
                "EvaluateTargetHealth": False
            }
        }
    )
    assert results == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alias_a_record_resolves():
    # The alias name is an invalid host and so should never resolve
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z1BKCTXD74EZPE",
                "DNSName": "localhost",
                "EvaluateTargetHealth": False
            }
        }
    )
    print(results)
    assert len(results) <= 2
    assert HostToScan("127.0.0.1", "a.dsd.io.") in results
    if len(results) == 2:
        assert HostToScan("::1", "a.dsd.io.") in results


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alias_cname_record_cant_resolve():
    # The alias name is an invalid host and so should never resolve
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "CNAME",
            "ResourceRecords": [
                {
                    "Value": "ijuwwi w902352 invalid name"
                }
            ]
        }
    )
    assert results == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alias_cname_record_resolves():
    # The alias name is an invalid host and so should never resolve
    results = await RecordResolver({}, False).resolve(
        {
            "Name": "a.dsd.io.",
            "Type": "CNAME",
            "ResourceRecords": [
                {
                    "Value": "localhost"
                },
                # This is yuck, I should be using patching to mock out the nslookup
                # instead I am relying on the build machine having internet access
                # and being able to resolve google
                {
                    "Value": "www.google.com"
                }
            ]
        }
    )
    assert len(results) > 1
    assert HostToScan("127.0.0.1", "a.dsd.io.") in results
    if HostToScan("::1", "a.dsd.io.") in results:
        assert len(results) > 2
