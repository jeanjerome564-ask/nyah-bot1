import time
import os
import alpaca_trade_api as tradeapi

print("Trading bot starting...")

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL

if not API_KEY or not API_SECRET:
    print("⚠️ Missing API credentials! Please set API_KEY and API_SECRET in Render Environment.")
    exit(1)

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Example trading loop
while True:
    try:
        # Get account info
        account = api.get_account()
        print(f"Account equity: {account.equity}")

        # Example: check AAPL price
        barset = api.get_bars("AAPL", "1Min", limit=1)
        price = barset[-1].c

        print(f"AAPL Price: {price}")

        # Example buy rule
        if float(price) < 150:  
            print("Buying 1 share of AAPL...")
            api.submit_order(
                symbol="AAPL",
                qty=1,
                side="buy",
                type="market",
                time_in_force="gtc"
            )

        time.sleep(60)  # wait 1 min before checking again

    except Exception as e:
        print(f"Error in trading loop: {e}")
        time.sleep(60)
