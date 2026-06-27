from .api import HiveEngineAPI


class HiveEngineTokens:
    def __init__(self, api=None):
        self.api = api or HiveEngineAPI()

    def get(self, symbol):
        return self.api.find_one(
            contract="tokens",
            table="tokens",
            query={"symbol": symbol}
        )
