import argparse
import os
import time
from datetime import datetime
from decimal import Decimal

from beem import Hive
from beem.hiveengine import (
    HiveEngineOrderBook,
    HiveEngineOrders,
    HiveEngineHistory,
    HiveEngineManager,
    TradingAdvisor,
    TradingConfig,
)
from beem.hiveengine.session import TradingSession


# ==========================================================
# CONFIG
# ==========================================================

ACCOUNT = "boobcat"
SYMBOL = "SWAP.BLURT"
ACTIVE_KEY = os.environ.get("BOOBCAT_ACTIVE_KEY")
AUTO = True          # False = Dry Run | True = Live
HARD_LIMIT = "1.0"


# ==========================================================
# MAIN
# ==========================================================

def run_once(session=None):

    if AUTO and not ACTIVE_KEY:
        raise SystemExit("Missing BOOBCAT_ACTIVE_KEY environment variable")

    hive = Hive(
        node=["https://api.hive.blog"],
        keys=[ACTIVE_KEY] if AUTO else [],
        nobroadcast=not AUTO,
        unsigned=not AUTO,
    )

    book = HiveEngineOrderBook()
    orders = HiveEngineOrders()
    history = HiveEngineHistory()
    manager = HiveEngineManager(hive)

    advisor = TradingAdvisor(
        TradingConfig(hard_limit=HARD_LIMIT)
    )

    my_orders = orders.buy_orders(ACCOUNT, SYMBOL)

    if not my_orders:
        print("No active buy order.")
        print()
        print("Create a small buy order on Hive Engine")
        print(f"Account : {ACCOUNT}")
        print(f"Market  : {SYMBOL}")
        return

    my_order = my_orders[0]

    best_bid = book.best_bid(SYMBOL)
    best_ask = book.best_ask(SYMBOL)
    last_trade = history.last_trade(SYMBOL)
    my_rank = book.my_buy_order(SYMBOL, ACCOUNT)

    rank = my_rank["rank"] if my_rank else 999

    my_price = Decimal(my_order["price"])
    best_bid_price = Decimal(best_bid["price"])

    suggested_price, reason = advisor.suggest_buy_price(
        best_bid["price"],
        best_ask["price"],
    )

    if session:
        session.update(
            rank=rank,
            my_account=ACCOUNT,
            best_bid_price=best_bid_price,
            best_bid_account=best_bid["account"],
        )

    # ==========================================================
    # OUTPUT
    # ==========================================================

    print("=" * 60)
    print("Hive Engine Trading Simulation")
    print("=" * 60)

    print(f"Time     : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Account  : {ACCOUNT}")
    print(f"Market   : {SYMBOL}")

    print("\nCURRENT ORDER")
    print("-" * 60)
    print(f"Rank     : #{rank}")
    print(f"ID       : {my_order['_id']}")
    print(f"Price    : {my_order['price']}")
    print(f"Quantity : {my_order['quantity']}")

    print("\nMARKET")
    print("-" * 60)
    print(f"Best Bid : {best_bid['price']} ({best_bid['account']})")
    print(f"Best Ask : {best_ask['price']} ({best_ask['account']})")
    print(f"Spread   : {book.spread(SYMBOL)}")

    print("\nLAST TRADE")
    print("-" * 60)
    print(f"Price    : {last_trade['price']}")
    print(f"Buyer    : {last_trade['buyer']}")
    print(f"Seller   : {last_trade['seller']}")

    print("\nANALYSIS")
    print("-" * 60)

    if rank == 1:
        print("Status   : BEST BID")
    else:
        print("Status   : OUTBID")
        print(f"Suggest  : {suggested_price}")

    # ==========================================================
    # SAFETY
    # ==========================================================

    if suggested_price is None:
        print("\nNo action required.")
        print(f"Reason   : {reason}")
        return

    if rank == 1:
        print("\nAlready best bid.")
        return

    if suggested_price <= my_price:
        print("\nAlready at suggested price.")
        return

    # ==========================================================
    # ACTION
    # ==========================================================

    if AUTO:

        print("\nLIVE MODE")
        print("-" * 60)

        result = manager.replace_buy(
            ACCOUNT,
            SYMBOL,
            my_order["quantity"],
            suggested_price,
        )

        print("Cancel:")
        print(result["cancel_tx"])

        print("\nNew Buy:")
        print(result["buy_tx"])

    else:

        print("\nACTION PLAN")
        print("-" * 60)

        plan = manager.replace_buy_plan(
            ACCOUNT,
            SYMBOL,
            my_order["quantity"],
            suggested_price,
        )

        print("Cancel:")
        print(plan["cancel"])

        print("\nNew Buy:")
        print(plan["new_buy"])

        print("\n*** DRY RUN ***")
        print("Nothing will be broadcast.")


# ==========================================================
# CLI
# ==========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--watch",
        type=int,
        default=0,
        help="Run every N seconds",
    )

    args = parser.parse_args()

    if args.watch <= 0:
        run_once()
        return

    session = TradingSession()

    print(f"Watching every {args.watch} seconds. Press Ctrl+C to stop.")

    try:

        while True:
            run_once(session)
            time.sleep(args.watch)

    except KeyboardInterrupt:
        print()
        session.summary()


if __name__ == "__main__":
    main()