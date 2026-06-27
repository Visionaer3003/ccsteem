from decimal import Decimal

from .config import TradingConfig


class TradingAdvisor:
    def __init__(self, config=None):
        self.config = config or TradingConfig()

    def _decimal(self, value):
        return Decimal(str(value))

    def suggest_buy_price(self, best_bid, best_ask):
        best_bid = self._decimal(best_bid)
        best_ask = self._decimal(best_ask)

        tick_size = self._decimal(self.config.tick_size)
        hard_limit = self._decimal(self.config.hard_limit)

        new_price = best_bid + tick_size

        if new_price >= best_ask:
            return None, "Spread too small"

        if new_price > hard_limit:
            return None, "Hard limit reached"

        return new_price, "OK"
