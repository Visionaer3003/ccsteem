from beem.hiveengine import HiveEngineOrderBook


def print_orders(title, orders, my_account=None):
    print()
    print(title)
    print("-" * 60)

    for i, order in enumerate(orders, start=1):
        marker = " <== YOU" if my_account and order["account"] == my_account else ""
        print(
            f"#{i:<2} "
            f"{order['account']:<16} "
            f"{order['price']:>12} "
            f"{order['quantity']:>14}"
            f"{marker}"
        )


def watch(symbol, my_account=None, limit=10):
    book = HiveEngineOrderBook()

    bid = book.best_bid(symbol)
    ask = book.best_ask(symbol)

    buy_orders = book.buy_orders(symbol, limit=limit)
    sell_orders = book.sell_orders(symbol, limit=limit)

    print("=" * 60)
    print(f"Market: {symbol}")
    print("=" * 60)

    if bid:
        print(f"Best Bid : {bid['price']} ({bid['account']})")
    else:
        print("Best Bid : None")

    if ask:
        print(f"Best Ask : {ask['price']} ({ask['account']})")
    else:
        print("Best Ask : None")

    if bid and ask:
        spread = float(ask["price"]) - float(bid["price"])
        mid = (float(ask["price"]) + float(bid["price"])) / 2
        print(f"Spread   : {spread:.8f}")
        print(f"Mid Price: {mid:.8f}")

    print_orders("BUY ORDERS", buy_orders, my_account)
    print_orders("SELL ORDERS", sell_orders, my_account)

    if my_account:
        my_order = book.my_buy_order(symbol, my_account)

        print()
        print("MY BUY ORDER")
        print("-" * 60)

        if my_order:
            print(f"Rank     : #{my_order['rank']}")
            print(f"Price    : {my_order['price']}")
            print(f"Quantity : {my_order['quantity']}")

            if bid:
                diff = float(bid["price"]) - float(my_order["price"])

                if diff == 0:
                    print("✅ You have the highest buy order.")
                else:
                    print(f"⚠️ Outbid by {bid['account']}")
                    print(f"Difference: {diff:.8f}")
        else:
            print("No active buy order found.")


if __name__ == "__main__":
    watch("SWAP.BLURT", "dagobert007", limit=10)
