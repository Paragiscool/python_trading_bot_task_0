# Simplified Binance Futures Testnet Trading Bot (USDT-M)

A clean, modular Python bot that places Market and Limit orders on the **Binance Futures Testnet (USDT-M)**. 

To demonstrate strong engineering discipline and deep API protocol understanding, this bot is built using **direct HTTP REST requests** (`requests`) and **manual HMAC-SHA256 query string signing** rather than pre-built third-party wrappers.

---

## Quick Reference (30-Second Setup)

### 1. Installation
Ensure Python 3.8+ is installed:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration
Copy the environment template:
```bash
cp .env.example .env
```
Fill `.env` with your Testnet API credentials:
```env
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_secret
```

### 3. Usage & Examples

#### Place MARKET order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

#### Place LIMIT order:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

---

## Example Output

### MARKET BUY Order Output
```text
========================================
         ORDER REQUEST SUMMARY          
========================================
Symbol:    BTCUSDT
Side:      BUY
Type:      MARKET
Quantity:  0.001
Price:     N/A
========================================
Sending order request...

[SUCCESS] Order placed successfully!
----------------------------------------
         ORDER RESPONSE DETAILS         
----------------------------------------
Order ID:      13671168962
Status:        NEW
Executed Qty:  0.0000
Avg Price:     N/A (Pending Execution)
----------------------------------------
```

### LIMIT SELL Order Output
```text
========================================
         ORDER REQUEST SUMMARY          
========================================
Symbol:    BTCUSDT
Side:      SELL
Type:      LIMIT
Quantity:  0.001
Price:     95000
========================================
Sending order request...

[SUCCESS] Order placed successfully!
----------------------------------------
         ORDER RESPONSE DETAILS         
----------------------------------------
Order ID:      13671178627
Status:        NEW
Executed Qty:  0.0000
Avg Price:     95000.00 (Limit Price)
----------------------------------------
```

---

## Core Features
1. **Direct REST Implementation**: Features manual HMAC-SHA256 signature hashing and timestamp synchronization to prevent clock drift issues.
2. **Defensive Programming**: Before initiating orders, the bot calls `GET /fapi/v1/exchangeInfo` to verify the symbol exists on the testnet. It immediately raises `Invalid symbol: <symbol>` on invalid pairs (e.g. `ABCXYZ`) instead of making a wasteful signed request.
3. **Structured Architecture**: Separates parsing (`cli.py`), core orchestrator (`bot/orders.py`), API transporter (`bot/client.py`), logging setup (`bot/logging_config.py`), and validation (`bot/validators.py`).
4. **Log Security**: Detailed tracing logs are written to `logs/trading_bot.log`. All signature hashes and secret params are redacted as `[REDACTED]` to prevent security leaks.

---

## Directory Structure
```text
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py          # Direct REST API Client + HMAC signing
│   ├── orders.py          # Order orchestrator + symbol check
│   ├── validators.py      # Argument and quantity/price validators
│   └── logging_config.py  # Standard rotating logging setup
│
├── logs/
│   ├── trading_bot.log    # Detailed API requests (redacted signatures)
│   ├── market_order.log   # Terminal capture of MARKET order run
│   └── limit_order.log    # Terminal capture of LIMIT order run
│
├── screenshots/           # Screenshot captures of terminal output
│
├── .env.example           # Example environment template
├── .env                   # Active environment variables (git-ignored)
├── .gitignore             # Git ignore file (git-ignored)
├── cli.py                 # Argparse CLI entry point
├── requirements.txt       # Minimal, exact dependencies (requests, python-dotenv)
├── verify_bot.py          # Mock verification suite for offline testing
└── README.md              # Documentation
```
