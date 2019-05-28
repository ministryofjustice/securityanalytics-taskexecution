import pytest
from itertools import islice
from dns_ingestor.scheduler import Scheduler


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
def test_one_bucket_one_answer():
    schedule = Scheduler(221, 100, 1)
    # the answer for this schedule should always be 321
    # i.e. the end of the last and only bucket
    # taking first 3 items to check
    assert all((321 == next_scan for next_scan in islice(schedule, 3)))


@pytest.mark.unit
def test_splits_period():
    schedule = Scheduler(221, 100, 10)
    # the answer for this schedule is a plan that covers the ends of 10 buckets
    # i.e. 231, 241, 251, ..., 321
    expected = range(231, 321+1, 10)
    actual = list(islice(schedule, 10))
    assert len(expected) == len(actual) and all([e == a for e, a in zip(expected, actual)])


@pytest.mark.unit
def test_wraps_around():
    schedule = Scheduler(10, 5, 10)
    # the answer for this schedule is a plan that covers the ends of 10 buckets
    # i.e. 10.5, 11, 11.5, ..., 15
    expected = [10 + x*0.5 for x in range(1, 10+1)]
    first_loop = list(islice(schedule, 10))
    second_loop = list(islice(schedule, 10))
    assert first_loop == expected and first_loop == second_loop
