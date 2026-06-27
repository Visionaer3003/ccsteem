from beem import Hive
from beem.hiveengine import (
    HiveEngineOrderBook,
    HiveEngineOrders,
    HiveEngineHistory,
    HiveEngineManager,
)


ACCOUNT = "dagobert007"
SYMBOL = "SWAP.BLURT"


def main():
    hive = Hive(
        node=["https://api.hive.blog"],
        nobroadcast=True,
        unsigned=True
    )

    book = HiveEngineOrderBook()
    orders = HiveEngineOrders()
    history = HiveEngineHistory()
    manager = HiveEngineManager(hive)

    my_orders = orders.buy_orders(ACCOUNT, SYMBOL)

    if not my_orders:
        print("No active buy order.")
        return

    my_order = my_orders[0]
    best_bid = book.best_bid(SYMBOL)
    best_ask = book.best_ask(SYMBOL)
    last_trade = history.last_trade(SYMBOL)

    print("=" * 60)
    print("Hive Engine Trading Simulation")
    print("=" * 60)

    print(f"Account : {ACCOUNT}")
    print(f"Market  : {SYMBOL}")

    print("\nCURRENT ORDER")
    print("-" * 60)
    print(f"ID       : {my_order['_id']}")
    print(f"Price    : {my_order['price']}")
    print(f"Quantity : {my_order['quantity']}")

    print("\nMARKET")
    print("-" * 60)
    print(f"Best Bid : {best_bid['price']} ({best_bid['account']})")
    print(f"Best Ask : {best_ask['price']} ({best_ask['account']})")

    spread = float(best_ask["price"]) - float(best_bid["price"])
    print(f"Spread   : {spread:.8f}")

    print("\nLAST TRADE")
    print("-" * 60)
    print(f"Price    : {last_trade['price']}")
    print(f"Buyer    : {last_trade['buyer']}")
    print(f"Seller   : {last_trade['seller']}")

    suggested_price = float(best_bid["price"]) + 0.00000001

    print("\nANALYSIS")
    print("-" * 60)

    if float(my_order["price"]) < float(best_bid["price"]):
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


if __name__ == "__main__":
    main()
