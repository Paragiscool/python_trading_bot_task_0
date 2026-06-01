# Advanced Binance Futures Testnet Trading Bot (USDT-M)

![Tests](https://github.com/Paragiscool/python_trading_bot_task_0/actions/workflows/tests.yml/badge.svg)
![Coverage](https://img.shields.io/badge/Coverage-90%25%2B-success.svg)
![Linting](https://img.shields.io/badge/Lint-Ruff%20Passing-success.svg)
![Types](https://img.shields.io/badge/Types-Mypy%20Passing-success.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)

## 📖 Overview
A professional-grade, modular Python trading bot that interacts directly with the **Binance Futures Testnet (USDT-M)**. Designed to demonstrate strong engineering discipline, it features an orchestrator pattern, automated retry logic for rate limits, structured JSON logging with correlation IDs, strict typing, and a complete Pytest suite.

---

## 🚀 Features
✓ **MARKET Orders**  
✓ **LIMIT Orders**  
✓ **STOP_LIMIT Orders**  
✓ **Account Information**  
✓ **Open Orders**  
✓ **Position Monitoring**  
✓ **Exchange Filter Validation**  
✓ **Structured Logging**  
✓ **Retry/Backoff Logic**  
✓ **Docker Support**  
✓ **CI/CD Pipelines**  
✓ **Type Checking (`mypy`)**  
✓ **Test Coverage (`pytest-cov`)**

---

## 🏛 Architecture Diagram

```text
┌─────────────────────┐
│      CLI Layer      │
│ argparse commands   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Orders Layer     │
│ Validation + Logic  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Binance REST API   │
│ HMAC Authentication │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Binance Testnet API │
└─────────────────────┘
```

---

## 🔄 Request Flow (Sequence Diagram)

```text
User
 │
 │ place order
 ▼
CLI Layer
 │
 ▼
Validator (bot/validators.py)
 │
 ▼
ExchangeInfo Cache (Local Filter Rules)
 │
 ▼
Order Orchestrator
 │
 ▼
REST Client (Injects UUID & Signs request)
 │
 ▼
Binance Futures Testnet
 │
 ▼ (429 Rate Limit)
REST Client (Exponential Backoff & Retry)
 │
 ▼ (200 OK)
Structured JSON Logger
 │
 ▼
CLI Output
```

---

## ⚙️ Quick Start

### 1. Configuration
```bash
cp .env.example .env
# Add your Testnet API credentials to .env
```

### 2. Local Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📸 Screenshots

### Interactive Menu
![Health](screenshots/health.png)

### Market Order Execution
![Market Order](screenshots/market_order.png)

### Account Dashboard
![Account](screenshots/account.png)

---

## 💻 Examples

The bot supports an interactive menu or direct CLI commands:

**Interactive Menu:**
```bash
python cli.py interactive
```

**Direct Execution:**
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
python cli.py account
python cli.py positions
python cli.py open-orders
```

*For more details, see [docs/API_REFERENCE.md](docs/API_REFERENCE.md).*

---

## ✅ Validation Coverage

| Scenario | Handled By | Result |
|-----------|-----------|---------|
| Invalid Symbol Format | `validators.py` | Local Exception |
| Order Price violates `tickSize` | `orders.py` | Local Exception |
| Order Qty violates `stepSize` | `orders.py` | Local Exception |
| HTTP 429 (Rate Limit) | `client.py` | Exponential Backoff Retry |
| HTTP 500+ (Server Error) | `client.py` | Exponential Backoff Retry |
| Network Timeout | `requests` | Bubble Up `BinanceNetworkError` |

---

## 📝 Logging Strategy

Our logging strategy is built for enterprise observability and traceability:

```text
Request Received
        ↓
Validation Rules Checked
        ↓
REST Request Dispatched
        ↓
Network Response (HTTP Status)
        ↓
Structured JSON Log Emitted
```

**Example Log Output:**
```json
{
  "timestamp": "2024-05-15T12:00:00Z",
  "level": "INFO",
  "event": "Received response: HTTP 200",
  "logger_name": "trading_bot",
  "request_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
}
```

---

## 🧪 Testing
The repository contains a robust Pytest suite checking signature logic, validation math, error handling, and orchestrator flows.
```bash
pytest --cov=bot
```

---

## 🐳 Docker Support
You can run the bot without installing Python locally:
```bash
docker build -t binance-bot .
docker run --env-file .env -it binance-bot interactive
```

---

## 🚀 CI/CD
This project utilizes GitHub Actions. On every push to the repository, the pipeline executes:
- `ruff check .`
- `mypy .`
- `pytest --cov=bot`

---

## 🛠 Design Decisions

This implementation intentionally uses direct REST requests instead of `python-binance` to demonstrate:
- **HMAC-SHA256 request signing**
- **Authentication handling**
- **Error management & resilient retries**
- **Strict exchange rule validation**
- **API abstraction design**

*For a deep dive into the architecture and tradeoffs, read [docs/DECISIONS.md](docs/DECISIONS.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).*

---

## 🔮 Future Improvements
- **WebSocket Integration**: Replace the REST polling for `orderStatus` and `accountInfo` with real-time WebSocket streams.
- **AsyncIO**: Migrate from the synchronous `requests` library to `httpx` and `asyncio` to handle hundreds of concurrent requests efficiently.
- **State Layer**: Introduce a lightweight local database (e.g., SQLite or Redis) to persist order states across bot restarts.

---

## 📊 Project Metrics

- **Python Files:** 12
- **Unit Tests:** 9
- **Coverage:** 90%+
- **Verified Execution Proofs:** See `proof/` directory for sanitized real-world API JSON responses.
