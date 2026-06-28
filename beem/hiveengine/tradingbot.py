import time
from decimal import Decimal, ROUND_DOWN
from datetime import datetime

from beem import Hive

from .advisor import TradingAdvisor
from .config import TradingConfig
from .manager import HiveEngineManager
from .orderbook import HiveEngineOrderBook
from .orders import HiveEngineOrders
from .logger import TradingLogger


class TradingBot:
    def __init__(
        self,
        account,
        symbol,
        active_key=None,
        node=None,
        hard_limit="1.0",
        auto=False,
        interval=60,
        budget=None,
        
    ):
        self.account = account
        self.symbol = symbol
        self.active_key = active_key
        self.node = node or ["https://api.hive.blog"]
        self.auto = auto
        self.interval = interval

        self.config = TradingConfig(hard_limit=hard_limit)
        self.advisor = TradingAdvisor(self.config)

        self.book = HiveEngineOrderBook()
        self.orders = HiveEngineOrders()
        self.budget = Decimal(str(budget)) if budget is not None else None
        self.logger = TradingLogger()
    
    def create_initial_buy(self):
        plan = self.create_initial_buy_plan()

        if not plan:
            return {
                "status": "NO_ACTION",
                "reason": "No valid initial buy plan",
            }

        hive = self._hive()
        manager = HiveEngineManager(hive)

        try:
            self.logger.info(
                f"Creating initial buy: "
                f"{plan['quantity']} {self.symbol} @ {plan['price']}"
            )

            tx = manager.market.buy(
                account=self.account,
                symbol=self.symbol,
                quantity=plan["quantity"],
                price=plan["price"],
            )

            self.logger.info(f"Transaction sent: {tx['trx_id']}")

        except Exception as e:
            self.logger.error(str(e))
            return {
                "status": "ERROR",
                "reason": str(e),
                "plan": plan,
            }

        return {
            "status": "INITIAL_BUY_CREATED",
            "plan": plan,
            "tx": tx,
        }
    
    def calculate_quantity(self, price):
        if self.budget is None:
            raise Exception("Budget required to calculate quantity")

        price = Decimal(str(price))
        if price <= 0:
            raise Exception("Price must be greater than zero")

        raw_quantity = self.budget / price

        token = self.book.api.find_one(
            contract="tokens",
            table="tokens",
            query={"symbol": self.symbol},
        )

        precision = int(token["precision"])
        quant = Decimal("1").scaleb(-precision)

        return raw_quantity.quantize(quant, rounding=ROUND_DOWN)

    def create_initial_buy_plan(self):
        best_bid = self.book.best_bid(self.symbol)
        best_ask = self.book.best_ask(self.symbol)

        price, reason = self.advisor.suggest_buy_price(
            best_bid["price"],
            best_ask["price"],
        )

        if price is None:
            return None

        quantity = self.calculate_quantity(price)

        return {
            "price": price,
            "quantity": quantity,
            "reason": reason,
            "best_bid": best_bid,
            "best_ask": best_ask,
        }       

    def _hive(self):
        if self.auto and not self.active_key:
            raise Exception("Active key required in auto mode")

        return Hive(
            node=self.node,
            keys=[self.active_key] if self.auto else [],
            nobroadcast=not self.auto,
            unsigned=not self.auto,
        )

    def check_once(self):
        self.logger.info(
            f"Checking {self.account} on {self.symbol}"
        )
        hive = self._hive()
        manager = HiveEngineManager(hive)

        my_orders = self.orders.buy_orders(self.account, self.symbol)

        if not my_orders:
            self.logger.info("No active buy order found.")
            result = {
                "status": "NO_ORDER",
                "message": "No active buy order.",
            }

            if self.budget is not None:
                result["initial_plan"] = self.create_initial_buy_plan()

                if self.auto:
                    result["initial_action"] = self.create_initial_buy()
                    result["status"] = result["initial_action"]["status"]

            return result    

        my_order = my_orders[0]
        my_rank = self.book.my_buy_order(self.symbol, self.account)
        best_bid = self.book.best_bid(self.symbol)
        best_ask = self.book.best_ask(self.symbol)

        rank = my_rank["rank"] if my_rank else 999

        my_price = Decimal(str(my_order["price"]))
        best_bid_price = Decimal(str(best_bid["price"]))

        suggested_price, reason = self.advisor.suggest_buy_price(
            best_bid["price"],
            best_ask["price"],
        )

        result = {
            "time": datetime.now(),
            "account": self.account,
            "symbol": self.symbol,
            "order": my_order,
            "rank": rank,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "suggested_price": suggested_price,
            "reason": reason,
            "auto": self.auto,
        }

        if suggested_price is None:
            result["status"] = "NO_ACTION"
            return result

        if rank == 1:
            result["status"] = "BEST_BID"
            return result

        if suggested_price <= my_price:
            result["status"] = "NO_ACTION"
            result["reason"] = "Already at or above suggested price"
            return result

        if self.auto:
            try:
                self.logger.info(
                    f"Replacing buy order {my_order['_id']} -> {suggested_price}"
                )

                action = manager.replace_buy(
                    self.account,
                    self.symbol,
                    my_order["quantity"],
                    suggested_price,
                )

                result["status"] = "REPLACED"
                result["action"] = action

            except Exception as e:
                self.logger.error(str(e))
                result["status"] = "ERROR"
                result["reason"] = str(e)
        else:
            plan = manager.replace_buy_plan(
                self.account,
                self.symbol,
                my_order["quantity"],
                suggested_price,
            )
            result["status"] = "DRY_RUN"
            result["plan"] = plan

        return result

    def print_result(self, result):
        self.logger.info("=" * 60)
        self.logger.info("Hive Engine Trading Bot")
        self.logger.info("=" * 60)

        self.logger.info(f"Time    : {result.get('time')}")
        self.logger.info(f"Account : {self.account}")
        self.logger.info(f"Market  : {self.symbol}")
        self.logger.info(f"Mode    : {'AUTO' if self.auto else 'DRY RUN'}")

        if result["status"] in ("NO_ORDER", "INITIAL_BUY_CREATED"):
            self.logger.info("\nNo active buy order.")

            plan = result.get("initial_plan")
            if plan:
                self.logger.info("\nINITIAL BUY PLAN")
                self.logger.info("-" * 60)
                self.logger.info(f"Best Bid : {plan['best_bid']['price']} ({plan['best_bid']['account']})")
                self.logger.info(f"Best Ask : {plan['best_ask']['price']} ({plan['best_ask']['account']})")
                self.logger.info(f"Price    : {plan['price']:.8f}")
                self.logger.info(f"Quantity : {plan['quantity']:.6f}")
                self.logger.info(f"Reason   : {plan['reason']}")

            action = result.get("initial_action")
            if action:
                self.logger.info("\nINITIAL ACTION")
                self.logger.info("-" * 60)
                self.logger.info(action["status"])
                self.logger.info(action.get("tx"))

            return

        order = result["order"]
        best_bid = result["best_bid"]
        best_ask = result["best_ask"]

        self.logger.info("\nCURRENT ORDER")
        self.logger.info("-" * 60)
        self.logger.info(f"Rank     : #{result['rank']}")
        self.logger.info(f"ID       : {order['_id']}")
        self.logger.info(f"Price    : {order['price']}")
        self.logger.info(f"Quantity : {order['quantity']}")

        self.logger.info("\nMARKET")
        self.logger.info("-" * 60)
        self.logger.info(f"Best Bid : {best_bid['price']} ({best_bid['account']})")
        self.logger.info(f"Best Ask : {best_ask['price']} ({best_ask['account']})")
        self.logger.info(f"Suggest  : {result['suggested_price']}")

        self.logger.info("\nSTATUS")
        self.logger.info("-" * 60)
        self.logger.info(result["status"])

        if "reason" in result:
            self.logger.info(f"Reason   : {result['reason']}")

    def run(self):
        while True:
            result = self.check_once()
            self.print_result(result)
            time.sleep(self.interval)
