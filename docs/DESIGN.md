# Architecture and Design Document

This document outlines the high-level architecture and the technical decisions made while building the Simplified Trading Bot.

## Architecture

The bot is designed using a layered architecture to ensure separation of concerns, testability, and maintainability.

```text
┌──────────────────────────┐
│        CLI Layer         │ (cli.py)
│  (Argparse, Interactive) │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       Orders Layer       │ (bot/orders.py, validators.py)
│ (Validation, Orchestration)│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       REST Client        │ (bot/client.py, logging_config.py)
│  (HMAC, Retries, Logs)   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       Binance API        │ (Binance Futures Testnet)
└──────────────────────────┘
```

1. **CLI Layer**: Responsible solely for user interaction and parsing arguments.
2. **Orders Layer**: Acts as the orchestrator. It manages local exchange filter validations, constructs the parameters, and coordinates API calls.
3. **REST Client**: The low-level HTTP transport layer. It handles HMAC-SHA256 signing, request correlation IDs, logging, and automated retry backoffs for `429` (Rate Limits) and `5xx` errors.

## Request Flow

1. **User Input**: The user issues a command via the CLI (e.g. `python cli.py place ...`).
2. **Argument Parsing**: `argparse` translates the command into a structured `Namespace`.
3. **Orchestration & Validation**: The `bot/orders.py` layer intercepts the request. It fetches the `/fapi/v1/exchangeInfo` rules for the symbol, applies math using `bot/validators.py` to ensure `stepSize` and `tickSize` are respected, and formats the payload.
4. **Transport**: `bot/client.py` injects a unique UUID, adds the timestamp, signs the request payload using HMAC-SHA256, and fires the HTTP request.
5. **Resilience**: If a transient network failure or rate limit occurs, the client autonomously backs off and retries.
6. **Response & Logging**: Success or failure is securely logged in structured JSON, and the CLI outputs the user-friendly result.

## Technical Tradeoffs

### 1. Direct REST Client vs. `python-binance`
**Decision:** We chose to implement a custom REST client over using the popular `python-binance` library.
**Rationale:** While a library abstracts complexity, building the client from scratch demonstrates a deep understanding of core engineering principles: HTTP protocol handling, cryptographic signing (HMAC-SHA256), timestamp synchronization, and rate-limit resilience. It also removes a heavy dependency.

### 2. Local Exchange Validation vs. Server Rejection
**Decision:** We proactively fetch `/fapi/v1/exchangeInfo` and enforce `PRICE_FILTER` and `LOT_SIZE` locally using precise `Decimal` math.
**Rationale:** Relying on the exchange to reject invalid orders consumes precious rate limits. Validating locally saves network bandwidth, prevents potential IP bans, and provides immediate feedback to the user.

### 3. Structured JSON Logging vs. Flat Text
**Decision:** Logs are emitted as structured JSON objects (with injected UUIDs) rather than traditional strings.
**Rationale:** In modern production systems, logs are aggregated into tools like Datadog, ELK, or Splunk. JSON logging allows these platforms to parse and index fields (like `request_id`, `status_code`, `symbol`) out of the box, making debugging distributed systems significantly easier.

## Security

- **No Hardcoded Keys**: API keys are strictly loaded via `.env` files which are excluded via `.gitignore`.
- **Log Redaction**: The REST client explicitly redacts the `signature` parameter from logged URLs to prevent leaking valid cryptographic signatures.
- **Dependency Minimization**: By writing the REST client manually, we reduce the surface area for supply-chain attacks.

## Error Handling and Resilience

- **Exponential Backoff**: If the bot encounters a HTTP `429` (Too Many Requests) or a server error (`500+`), it enters a retry loop. It will honor the `Retry-After` header if present, or fallback to an exponential backoff algorithm (`time.sleep(2 ** attempt)`).
- **Network Timeouts**: Requests are strictly bound by a 10-second timeout to prevent the bot from hanging indefinitely during network partitions.
- **Traceability**: Every HTTP request is tagged with a unique `uuid4` as a `request_id`. This ID binds the request, response, and error logs together, making it trivial to trace the exact lifecycle of a failed order.

## Future Improvements

If we were to expand this into a high-frequency or multi-exchange bot, the following upgrades would be necessary:
- **WebSocket Integration**: Replace the REST polling for `orderStatus` and `accountInfo` with real-time WebSocket streams.
- **AsyncIO**: Migrate from the synchronous `requests` library to `httpx` and `asyncio` to handle hundreds of concurrent requests efficiently.
- **Database/State Layer**: Introduce a lightweight local database (e.g., SQLite or Redis) to persist order states across bot restarts.
