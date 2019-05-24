import decimal


# This class is used to distribute the hosts to scan across the time available
class Scheduler:
    def __init__(self, start_time, planning_period, buckets):
        self.start_time = start_time
        self.end_time = start_time + planning_period
        self.increment = (self.end_time - start_time) / buckets
        self.next_slot = start_time + self.increment

    def use_slot(self):
        self.next_slot += self.increment
        if self.next_slot > self.end_time:
            self.next_slot = self.start_time + self.increment

    def next_planned_slot(self):
        return decimal.Decimal(self.next_slot)
