from decimal import Decimal

from .tokens import HiveEngineTokens


class HiveEngineFormatter:
    def __init__(self, api=None):
        self.tokens = HiveEngineTokens(api)

    def decimal(self, value):
        return Decimal(str(value))

    def format_quantity(self, symbol, value):
        token = self.tokens.get(symbol)

        if not token:
            raise Exception(f"Unknown token: {symbol}")

        precision = int(token["precision"])
        quant = Decimal("1").scaleb(-precision)

        return str(self.decimal(value).quantize(quant))
