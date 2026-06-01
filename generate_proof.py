import os
import json
from dotenv import load_dotenv
from bot.client import BinanceFuturesRESTClient

def sanitize(data):
    if isinstance(data, dict):
        # Recursively sanitize dictionary keys/values
        return {k: sanitize(v) for k, v in data.items() if k not in ["updateTime", "clientOrderId"]}
    elif isinstance(data, list):
        return [sanitize(i) for i in data]
    return data

def save_proof(filename, data):
    os.makedirs("proof", exist_ok=True)
    with open(f"proof/{filename}", "w") as f:
        json.dump(sanitize(data), f, indent=2)
    print(f"Saved proof/{filename}")

if __name__ == "__main__":
    load_dotenv()
    client = BinanceFuturesRESTClient(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET")
    )

    # 1. Health
    health = client._send_request("GET", "/fapi/v1/ping")
    save_proof("health_response.json", {"ping": "success", "serverTime": client.get_server_time()})

    # 2. Account
    account = client.get_account_info()
    save_proof("account_response.json", account)

    # 3. Market Order
    market = client.place_order("BTCUSDT", "BUY", "MARKET", 0.001)
    save_proof("market_order_response.json", market)

    # 4. Limit Order
    limit = client.place_order("BTCUSDT", "SELL", "LIMIT", 0.001, price=150000)
    save_proof("limit_order_response.json", limit)

    print("All proofs generated.")
