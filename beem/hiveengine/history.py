from .api import HiveEngineAPI


class HiveEngineHistory:
    def __init__(self, api=None):
        self.api = api or HiveEngineAPI()

    def trades(self, symbol, limit=100):
        rows = self.api.find(
            contract="market",
            table="tradesHistory",
            query={"symbol": symbol},
            limit=limit,
            indexes=[{"index": "timestamp", "descending": True}]
        )

        return sorted(rows, key=lambda row: row.get("timestamp", 0), reverse=True)

    def last_trade(self, symbol):
        rows = self.trades(symbol, limit=100)
        return rows[0] if rows else None

    def last_price(self, symbol):
        trade = self.last_trade(symbol)
        return float(trade["price"]) if trade else None

    def volume(self, symbol, limit=100):
        rows = self.trades(symbol, limit=limit)
        return sum(float(row.get("quantity", 0)) for row in rows)

    def average_price(self, symbol, limit=100):
        rows = self.trades(symbol, limit=limit)
        if not rows:
            return None

        total_quantity = sum(float(row.get("quantity", 0)) for row in rows)
        if total_quantity == 0:
            return None

        total_value = sum(
            float(row.get("quantity", 0)) * float(row.get("price", 0))
            for row in rows
        )

        return total_value / total_quantity
