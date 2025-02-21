class ProfitMessage:
    def __init__(self, profit_growth: list[float]):
        self.profit_growth = profit_growth
        self.profit = [sum(self.profit_growth[:i + 1]) for i in range(len(self.profit_growth))]

    def to_dict(self):
        return {
            "profit_growth": self.profit_growth,
            "profit": self.profit
        }
