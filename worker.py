import time
import os

print("Trading bot starting...")

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
    print("⚠️ Missing API credentials! Please set API_KEY and API_SECRET in Render Environment.")
    exit(1)

# Example trading loop
while True:
    try:
        # TODO: replace this with your broker API call (Alpaca, Binance, etc.)
        print("Checking markets...")

        # Example placeholder logic
        # price = get_price("AAPL")  
        # if price < 150:
        #     place_order("AAPL", "buy", 1)

        time.sleep(30)  # wait before checking again

    except Exception as e:
        print(f"Error in trading loop: {e}")
        time.sleep(60)
