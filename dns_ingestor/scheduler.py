import decimal


# This class is used to distribute the hosts to scan across the time available
class Scheduler:
    def __init__(self, start_time, planning_period, buckets):
        if not all((isinstance(param, int) and param > 0 for param in (planning_period, buckets))):
            raise TypeError("The planning period and number of buckets must be positive integer values")
        self.next_slot = self.start_time = start_time
        self.end_time = start_time + planning_period
        self.increment = (self.end_time - start_time) / buckets

    def __iter__(self):
        return self

    def __next__(self):
        self.next_slot += self.increment
        if self.next_slot > self.end_time:
            self.next_slot = self.start_time + self.increment
        return decimal.Decimal(self.next_slot)
