from decimal import Decimal


class TradingConfig:
    def __init__(
        self,
        tick_size="0.00000001",
        hard_limit="1.0",
        min_spread="0.00000001",
        max_price_mode="smart",
    ):
        self.tick_size = Decimal(str(tick_size))
        self.hard_limit = Decimal(str(hard_limit))
        self.min_spread = Decimal(str(min_spread))
        self.max_price_mode = max_price_mode
