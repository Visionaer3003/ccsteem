from .api import HiveEngineAPI


class HiveEngineWallet:
    def __init__(self, api=None):
        self.api = api or HiveEngineAPI()

    def balances(self, account, limit=1000):
        return self.api.find(
            contract="tokens",
            table="balances",
            query={"account": account},
            limit=limit
        )

    def balance(self, account, symbol):
        return self.api.find_one(
            contract="tokens",
            table="balances",
            query={
                "account": account,
                "symbol": symbol
            }
        )
