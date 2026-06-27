class HiveEngineMarket:
    CUSTOM_JSON_ID = "ssc-mainnet-hive"

    def __init__(self, hive):
        self.hive = hive

    def _broadcast(self, account, contract_action, payload):
        data = {
            "contractName": "market",
            "contractAction": contract_action,
            "contractPayload": payload
        }

        return self.hive.custom_json(
            self.CUSTOM_JSON_ID,
            data,
            required_posting_auths=[account]
        )

    def buy(self, account, symbol, quantity, price):
        return self._broadcast(account, "buy", {
            "symbol": symbol,
            "quantity": f"{float(quantity):.8f}",
            "price": f"{float(price):.8f}"
        })

    def sell(self, account, symbol, quantity, price):
        return self._broadcast(account, "sell", {
            "symbol": symbol,
            "quantity": f"{float(quantity):.8f}",
            "price": f"{float(price):.8f}"
        })

    def cancel(self, account, order_id, order_type):
        return self._broadcast(account, "cancel", {
            "type": order_type,
            "id": str(order_id)
        })
