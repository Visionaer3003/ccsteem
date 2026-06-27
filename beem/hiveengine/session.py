from collections import Counter
from datetime import datetime


class TradingSession:
    def __init__(self):
        self.started = datetime.now()
        self.checks = 0
        self.bestbid = 0
        self.outbid = 0
        self.best_rank = 999
        self.worst_rank = 0
        self.rank_history = []
        self.price_history = []
        self.opponents = Counter()

    def update(self, rank, my_account, best_bid_price, best_bid_account):
        self.checks += 1
        self.rank_history.append(rank)
        self.price_history.append(best_bid_price)

        self.best_rank = min(self.best_rank, rank)
        self.worst_rank = max(self.worst_rank, rank)

        if rank == 1:
            self.bestbid += 1
        else:
            self.outbid += 1
            if best_bid_account != my_account:
                self.opponents[best_bid_account] += 1

    @property
    def average_rank(self):
        if not self.rank_history:
            return 0
        return sum(self.rank_history) / len(self.rank_history)

    def summary(self):
        runtime = datetime.now() - self.started

        print()
        print("=" * 60)
        print("Simulation Summary")
        print("=" * 60)
        print(f"Runtime      : {runtime}")
        print(f"Checks       : {self.checks}")

        print()
        print(f"Best Bid     : {self.bestbid}")
        print(f"Outbid       : {self.outbid}")

        print()
        print(f"Best Rank    : {self.best_rank}")
        print(f"Worst Rank   : {self.worst_rank}")
        print(f"Average Rank : {self.average_rank:.2f}")

        print()
        print("Top Opponents")
        print("-" * 60)
        for account, count in self.opponents.most_common(10):
            print(f"{account:<20}{count}")

        print("=" * 60)
