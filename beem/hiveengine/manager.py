from decimal import Decimal
from .orders import HiveEngineOrders
from .utils import HiveEngineFormatter


class HiveEngineManager:
    CUSTOM_JSON_ID = "ssc-mainnet-hive"

    def __init__(self, hive):
        self.hive = hive
        self.orders = HiveEngineOrders()
        self.formatter = HiveEngineFormatter()

    def _custom_json_payload(self, action, payload):
        return {
            "id": self.CUSTOM_JSON_ID,
            "json": {
                "contractName": "market",
                "contractAction": action,
                "contractPayload": payload
            }
        }

    def replace_buy_plan(self, account, symbol, quantity, new_price):
        current = self.orders.buy_orders(account, symbol)

        if not current:
            raise Exception("No active buy order found.")

        order = current[0]

        return {
            "old_order": order,
            "cancel": self._custom_json_payload("cancel", {
                "type": "buy",
                "id": str(order["_id"])
            }),
            "new_buy": self._custom_json_payload("buy", {
                "symbol": symbol,
                "quantity": self.formatter.format_quantity(symbol, quantity),
                "price": f"{Decimal(str(new_price)):.8f}"
            })
        }
