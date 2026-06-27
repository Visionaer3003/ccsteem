import argparse
import time
from datetime import datetime

from beem import Hive
from beem.hiveengine import (
    HiveEngineOrderBook,
    HiveEngineOrders,
    HiveEngineHistory,
    HiveEngineManager,
)
from beem.hiveengine.session import TradingSession

ACCOUNT = "dagobert007"
SYMBOL = "SWAP.BLURT"
INCREMENT = 0.00000001


def run_once(session=None):
    hive = Hive(node=["https://api.hive.blog"], nobroadcast=True, unsigned=True)

    book = HiveEngineOrderBook()
    orders = HiveEngineOrders()
    history = HiveEngineHistory()
    manager = HiveEngineManager(hive)

    my_orders = orders.buy_orders(ACCOUNT, SYMBOL)
    if not my_orders:
        print("No active buy order.")
        return

    my_order = my_orders[0]
    my_rank_order = book.my_buy_order(SYMBOL, ACCOUNT)

    best_bid = book.best_bid(SYMBOL)
    best_ask = book.best_ask(SYMBOL)
    last_trade = history.last_trade(SYMBOL)

    my_price = float(my_order["price"])
    best_bid_price = float(best_bid["price"])
    suggested_price = best_bid_price + INCREMENT

    rank = my_rank_order["rank"] if my_rank_order else 999

    session.update(
        rank=rank,
        my_account=ACCOUNT,
        best_bid_price=best_bid_price,
        best_bid_account=best_bid["account"],
    )

    print("=" * 60)
    print(f"Hive Engine Trading Simulation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"Account : {ACCOUNT}")
    print(f"Market  : {SYMBOL}")

    print("\nCURRENT ORDER")
    print("-" * 60)
    print(f"ID       : {my_order['_id']}")
    print(f"Rank     : #{rank}")
    print(f"Price    : {my_order['price']}")
    print(f"Quantity : {my_order['quantity']}")

    print("\nMARKET")
    print("-" * 60)
    print(f"Best Bid : {best_bid['price']} ({best_bid['account']})")
    print(f"Best Ask : {best_ask['price']} ({best_ask['account']})")
    print(f"Spread   : {float(best_ask['price']) - best_bid_price:.8f}")

    print("\nLAST TRADE")
    print("-" * 60)
    print(f"Price    : {last_trade['price']}")
    print(f"Buyer    : {last_trade['buyer']}")
    print(f"Seller   : {last_trade['seller']}")

    print("\nANALYSIS")
    print("-" * 60)
    if my_price < best_bid_price:
        print("Status   : OUTBID")
        print(f"Suggest  : {suggested_price:.8f}")
    else:
        print("Status   : BEST BID")

    plan = manager.replace_buy_plan(
        ACCOUNT,
        SYMBOL,
        float(my_order["quantity"]),
        suggested_price,
    )

    print("\nACTION PLAN")
    print("-" * 60)
    print("Cancel:")
    print(plan["cancel"])
    print("\nNew Buy:")
    print(plan["new_buy"])

    print("\n*** DRY RUN ***")
    print("Nothing will be broadcast.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", type=int, default=0, help="repeat every N seconds")
    args = parser.parse_args()

    if args.watch <= 0:
        run_once()
        return

    session = TradingSession()

    print(f"Starting dry-run watch mode every {args.watch} seconds. Press Ctrl+C to stop.")

    try:
        while True:
            run_once(session=session)
            time.sleep(args.watch)
    except KeyboardInterrupt:
        session.summary()


if __name__ == "__main__":
    main()
