from .api import HiveEngineAPI


class HiveEngineOrders:
    def __init__(self, api=None):
        self.api = api or HiveEngineAPI()

    def buy_orders(self, account, symbol=None, limit=1000):
        query = {"account": account}
        if symbol:
            query["symbol"] = symbol

        return self.api.find(
            contract="market",
            table="buyBook",
            query=query,
            limit=limit
        )

    def sell_orders(self, account, symbol=None, limit=1000):
        query = {"account": account}
        if symbol:
            query["symbol"] = symbol

        return self.api.find(
            contract="market",
            table="sellBook",
            query=query,
            limit=limit
        )

    def all(self, account, symbol=None):
        return {
            "buy": self.buy_orders(account, symbol),
            "sell": self.sell_orders(account, symbol)
        }
