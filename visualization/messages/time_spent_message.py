class TimeSpentMessage:
    def __init__(self, total_time_spent: list[int], total_waiting_time: list[int], num_customer_agens: int):
        self.total_time_spent = total_time_spent
        self.avg_time_spent = [time / num_customer_agens for time in total_time_spent]
        self.total_waiting_time = total_waiting_time
        self.avg_waiting_time = [time / num_customer_agens for time in total_waiting_time]

    def to_dict(self):
        return {
            "total_time_spent": self.total_time_spent,
            "avg_time_spent": self.avg_time_spent,
            "total_waiting_time": self.total_waiting_time,
            "avg_waiting_time": self.avg_waiting_time
        }
