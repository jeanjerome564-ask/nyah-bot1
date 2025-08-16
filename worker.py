import time
import os
import robin_stocks.robinhood as r

print("Trading bot starting...")

# Get credentials from Render environment
USERNAME = os.getenv("ROBINHOOD_USERNAME")
PASSWORD = os.getenv("ROBINHOOD_PASSWORD")

if not USERNAME or not PASSWORD:
    print("⚠️ Missing Robinhood credentials! Please set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in Render Environment.")
    exit(1)

# Login to Robinhood
try:
    r.login(USERNAME, PASSWORD)
    print("✅ Logged into Robinhood successfully.")
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

# Example trading loop
while True:
    try:
        print("Checking markets...")

        # Example: check AAPL price
        stock_data = r.stocks.get_latest_price("AAPL")
        price = float(stock_data[0])
        print(f"AAPL price: {price}")

        # Example rule: Buy if price < 150
        if price < 150:
            print("📈 Placing BUY order for AAPL...")
            r.orders.order_buy_market("AAPL", 1)

        time.sleep(60)  # wait before checking again

    except Exception as e:
        print(f"Error in trading loop: {e}")
        time.sleep(120)
