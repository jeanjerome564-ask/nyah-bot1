import time
import os
from alpaca_trade_api.rest import REST, TimeFrame

print("Trading bot starting...")

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"  # free paper trading env

if not API_KEY or not API_SECRET:
    print("⚠️ Missing API credentials! Please set API_KEY and API_SECRET in Render Environment.")
    exit(1)

api = REST(API_KEY, API_SECRET, base_url=BASE_URL)

# Example trading loop
while True:
    try:
        barset = api.get_bars("AAPL", TimeFrame.Minute, limit=1)
        last_close = barset[0].c  # latest close price
        print(f"Last AAPL close: {last_close}")

        # Example strategy
        if last_close < 150:
            print("Buying 1 share of AAPL 🚀")
            api.submit_order(symbol="AAPL", qty=1, side="buy", type="market", time_in_force="gtc")

        time.sleep(60)

    except Exception as e:
        print(f"Error in trading loop: {e}")
        time.sleep(60)
