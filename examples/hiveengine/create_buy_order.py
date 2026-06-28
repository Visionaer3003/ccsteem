import os

from beem import Hive
from beem.hiveengine import HiveEngineMarket

# ==========================================================
# CONFIG
# ==========================================================

ACCOUNT = "boobcat"
ACTIVE_KEY = os.environ.get("BOOBCAT_ACTIVE_KEY")
SYMBOL = "SWAP.BLURT"

PRICE = "0.01580000"
QUANTITY = "60.000000"

# ==========================================================

if not ACTIVE_KEY:
    raise SystemExit("Missing BOOBCAT_ACTIVE_KEY environment variable")

hive = Hive(
    node=["https://api.hive.blog"],
    keys=[ACTIVE_KEY],
)

market = HiveEngineMarket(hive)

print("=" * 60)
print("Create Hive Engine Buy Order")
print("=" * 60)

print(f"Account : {ACCOUNT}")
print(f"Market  : {SYMBOL}")
print(f"Price   : {PRICE}")
print(f"Quantity: {QUANTITY}")

answer = input("\nCreate order? (y/N): ")

if answer.lower() != "y":
    print("Cancelled.")
    raise SystemExit

tx = market.buy(
    account=ACCOUNT,
    symbol=SYMBOL,
    quantity=QUANTITY,
    price=PRICE,
)

print("\nTransaction created:")
print(tx)