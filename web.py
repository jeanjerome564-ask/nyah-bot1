from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return f"""
    <h2>Trading Bot Status</h2>
    <p>Bot is running ✅</p>
    <p>API_KEY: {os.getenv("API_KEY", "Not Set")[:4]}****</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
