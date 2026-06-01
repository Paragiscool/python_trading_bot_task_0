# Advanced Binance Futures Testnet Trading Bot (USDT-M)

![Tests](https://github.com/Paragiscool/python_trading_bot_task_0/actions/workflows/tests.yml/badge.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)

A professional-grade, modular Python trading bot that interacts directly with the **Binance Futures Testnet (USDT-M)**. Designed to demonstrate strong engineering discipline, it uses direct REST requests (`requests`) with manual HMAC-SHA256 signing, strict local exchange filter validation, structured JSON logging, and a complete Pytest suite.

---

## 🌟 Core Engineering Upgrades

1. **Local Exchange Rule Enforcement**: Before placing orders, the bot dynamically fetches `/fapi/v1/exchangeInfo` to enforce `LOT_SIZE` (`stepSize`, `minQty`) and `PRICE_FILTER` (`tickSize`, `minPrice`) locally. This prevents rate-limit penalties from bad requests.
2. **Advanced Order Types**: Full support for `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
3. **Robust CLI & Interactive UX**: Built with `argparse` subparsers. Supports commands for placing orders, checking health, querying status, canceling orders, and an **Interactive Trading Menu**.
4. **Structured JSON Logging**: Logs are strictly formatted in JSON via a custom `logging.Formatter` to simulate enterprise-grade log aggregation pipelines.
5. **DevOps & CI/CD**: Fully Dockerized with an automated GitHub Actions CI pipeline running the `pytest` test suite on every push.

---

## 🚀 Quick Start (Local & Docker)

### 1. Configuration
Copy the environment template:
```bash
cp .env.example .env
```
Fill `.env` with your Testnet API credentials:
```env
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_secret
```

### 2. Local Installation
Ensure Python 3.12+ is installed:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Docker Installation
You can run the bot without installing Python locally:
```bash
docker build -t binance-bot .
docker run --env-file .env -it binance-bot interactive
```

---

## 💻 CLI Usage

The bot supports several subcommands: `place`, `status`, `cancel`, `health`, and `interactive`.

### Interactive Mode (Recommended)
An interactive guided menu to seamlessly place, check, and cancel orders:
```bash
python cli.py interactive
```

### Health Check
Verify API connectivity and credential validity:
```bash
python cli.py health
```

### Place Orders
**MARKET Buy:**
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**LIMIT Sell:**
```bash
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

**STOP_LIMIT Order:**
```bash
python cli.py place --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 96000 --stop-price 95500
```

### Check Order Status
```bash
python cli.py status --symbol BTCUSDT --order-id 123456789
```

### Cancel Order
```bash
python cli.py cancel --symbol BTCUSDT --order-id 123456789
```

---

## 🧪 Testing

The repository contains a robust Pytest suite checking signature logic, validation math, error handling, and orchestrator flows.

```bash
# Run the test suite locally
pytest
```

---

## 📂 Directory Structure
```text
trading_bot/
│
├── .github/workflows/
│   └── tests.yml          # CI Pipeline
├── bot/
│   ├── client.py          # Direct REST API Client + HMAC signing
│   ├── orders.py          # Order orchestrator + symbol check
│   ├── validators.py      # Argument and quantity/price/filter validators
│   └── logging_config.py  # Structured JSON Rotating logging setup
│
├── tests/
│   ├── test_api_errors.py
│   ├── test_orders.py
│   ├── test_signature.py
│   └── test_validation.py
│
├── logs/
│   └── trading_bot.log    # JSON Structured Log File
│
├── Dockerfile             # Container definition
├── cli.py                 # Argparse CLI entry point
├── requirements.txt       # Dependencies (requests, python-dotenv, pytest)
└── README.md              # Documentation
```
