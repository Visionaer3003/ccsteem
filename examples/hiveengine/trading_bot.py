bot = TradingBot(
    account="boobcat",
    symbol="SWAP.BLURT",
    budget="5",
    hard_limit="0.020",
    auto=True,
)

bot.run()