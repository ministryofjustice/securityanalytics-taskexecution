import pytest
from itertools import islice
from dns_ingestor.scheduler import Scheduler
from unittest.mock import patch
from decimal import Decimal


@pytest.mark.unit
def test_type_checks():
    # fractional bucket
    with pytest.raises(TypeError):
        Scheduler(500, 100, 0.5)

    # negative bucket
    with pytest.raises(TypeError):
        Scheduler(500, 100, -3)

    # fractional period
    with pytest.raises(TypeError):
        Scheduler(500, 10.5, 2)

    # negative period
    with pytest.raises(TypeError):
        Scheduler(500, -10, 2)


@pytest.mark.unit
@patch("random.uniform", side_effect=[10, 24, 9])
def test_one_bucket_one_answer(_):
    schedule = Scheduler(221, 100, 1)
    # the answer for this schedule should always be 221
    # i.e. the start of the only bucket
    # taking first 3 items to check
    assert [Decimal(x) for x in [231, 245, 230]] == list(islice(schedule, 3))


@pytest.mark.unit
@patch("random.uniform", return_value=0)
def test_splits_period(_):
    schedule = Scheduler(221, 100, 10)
    # the answer for this schedule is a plan that covers the starts of 10 buckets
    # i.e. 221, 241, 251, ..., 311
    expected = range(221, 321, 10)
    actual = list(islice(schedule, 10))
    assert len(expected) == len(actual) and all([e == a for e, a in zip(expected, actual)])


@pytest.mark.unit
@patch("random.uniform", return_value=0)
def test_wraps_around(_):
    schedule = Scheduler(10, 5, 10)
    # the answer for this schedule is a plan that covers the starts of 10 buckets
    # i.e. 10, 10.5, 11, 11.5, ..., 14.5
    expected = [10 + x*0.5 for x in range(0, 10)]
    first_loop = list(islice(schedule, 10))
    second_loop = list(islice(schedule, 10))
    assert first_loop == expected and first_loop == second_loop
