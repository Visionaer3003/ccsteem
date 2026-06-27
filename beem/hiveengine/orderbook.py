from decimal import Decimal

from .api import HiveEngineAPI


class HiveEngineOrderBook:
    def __init__(self, api=None):
        self.api = api or HiveEngineAPI()

    def _decimal(self, value):
        return Decimal(str(value))

    def buy_orders(self, symbol, limit=100):
        return self.api.find(
            contract="market",
            table="buyBook",
            query={"symbol": symbol},
            limit=limit,
            indexes=[{"index": "priceDec", "descending": True}]
        )

    def sell_orders(self, symbol, limit=100):
        return self.api.find(
            contract="market",
            table="sellBook",
            query={"symbol": symbol},
            limit=limit,
            indexes=[{"index": "priceDec", "descending": False}]
        )

    def best_bid(self, symbol):
        orders = self.buy_orders(symbol, 1)
        return orders[0] if orders else None

    def best_ask(self, symbol):
        orders = self.sell_orders(symbol, 1)
        return orders[0] if orders else None

    def spread(self, symbol):
        bid = self.best_bid(symbol)
        ask = self.best_ask(symbol)
        if not bid or not ask:
            return None
        return self._decimal(ask["price"]) - self._decimal(bid["price"])

    def mid_price(self, symbol):
        bid = self.best_bid(symbol)
        ask = self.best_ask(symbol)
        if not bid or not ask:
            return None
        return (self._decimal(bid["price"]) + self._decimal(ask["price"])) / Decimal("2")

    def my_buy_order(self, symbol, account):
        orders = self.buy_orders(symbol, limit=1000)

        for i, order in enumerate(orders, start=1):
            if order["account"] == account:
                order = order.copy()
                order["rank"] = i
                return order

        return None
