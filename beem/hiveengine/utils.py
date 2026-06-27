from .tokens import HiveEngineTokens


class HiveEngineFormatter:
    def __init__(self, api=None):
        self.tokens = HiveEngineTokens(api)

    def format_quantity(self, symbol, value):
        token = self.tokens.get(symbol)

        if not token:
            raise Exception(f"Unknown token: {symbol}")

        precision = token["precision"]

        return f"{float(value):.{precision}f}"
