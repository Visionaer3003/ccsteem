from datetime import datetime


class TradingLogger:
    def info(self, message):
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] INFO  {message}")

    def warning(self, message):
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] WARN  {message}")

    def error(self, message):
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ERROR {message}")
