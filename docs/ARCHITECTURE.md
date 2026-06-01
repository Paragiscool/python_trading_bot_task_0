# System Architecture

The trading bot leverages a decoupled, layered architecture to separate user interaction, business logic, and transport transport mechanisms.

## Layered Design

```text
┌─────────────────────┐
│      CLI Layer      │ (cli.py)
│ argparse commands   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Orders Layer     │ (bot/orders.py)
│ Validation + Logic  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Binance REST API   │ (bot/client.py)
│ HMAC Authentication │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Binance Testnet API │ (https://testnet.binancefuture.com)
└─────────────────────┘
```

## Request Execution Sequence

This sequence diagram illustrates the lifecycle of a single order placement from the user to the Binance server and back, demonstrating the robust error handling and validation layers.

```text
User
 │
 │ place order (CLI)
 ▼
CLI Layer (argparse)
 │
 ▼
Validator (bot/validators.py)
 │
 ▼
ExchangeInfo Rules Check (bot/orders.py)
 │
 ▼
Order Orchestrator
 │
 ▼
REST Client (bot/client.py)
 │  - Inject Correlation ID (UUID)
 │  - Add Timestamp
 │  - Sign Request (HMAC-SHA256)
 ▼
Binance Futures Testnet
 │
 ▼ (Transient Error 429)
REST Client
 │  - Intercept 429
 │  - Apply Exponential Backoff
 ▼
Binance Futures Testnet
 │
 ▼ (200 OK)
Structured JSON Logger
 │
 ▼
CLI Output (Success)
```

## Logging Lifecycle

Our logging strategy is built for enterprise observability:

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

Example output:
```json
{
  "timestamp": "2024-05-15T12:00:00Z",
  "level": "INFO",
  "event": "Received response: HTTP 200",
  "logger_name": "trading_bot",
  "filename": "client.py",
  "line_number": 82,
  "request_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
}
```
