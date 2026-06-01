# Engineering Decisions

This document outlines the core engineering tradeoffs and design choices made during the development of this Simplified Trading Bot.

## 1. REST Client vs. Official SDK (`python-binance`)
**Decision:** Implement a custom REST client from scratch using `requests`.
**Rationale:** While leveraging a community library like `python-binance` saves time, it abstracts away critical elements of building reliable financial software. By writing a custom client, this project demonstrates:
- Mastery of the HTTP protocol and underlying transport mechanisms.
- The ability to implement secure cryptographic signing (HMAC-SHA256).
- Control over exact timeout parameters, connection pooling, and retry logic.

## 2. Exponential Backoff and Retries
**Decision:** Implement autonomous, in-client retry logic for HTTP `429` (Rate Limits) and `5xx` (Server Errors).
**Rationale:** In high-frequency or distributed environments, network partitions and rate limits are inevitable. A resilient client must not crash the orchestrator on a transient failure. The bot will automatically respect the server's `Retry-After` header or fall back to an exponential backoff (`time.sleep(2 ** attempt)`).

## 3. Local Exchange Filter Validation
**Decision:** Proactively fetch and cache `/fapi/v1/exchangeInfo` to enforce rules locally (e.g. `tickSize`, `stepSize`) before transmitting the order to Binance.
**Rationale:** Relying on Binance to reject malformed orders (like sending `0.0000000001` BTC) consumes API rate limit weight. By performing strict Decimal math locally, we save bandwidth, prevent potential IP bans for spamming bad requests, and provide the user with instantaneous error feedback.

## 4. Request Correlation IDs
**Decision:** Inject a unique `uuid4` into every API request and log entry.
**Rationale:** Tracing an order lifecycle through a distributed system is impossible without correlation IDs. By tagging every request with an ID, we simulate a microservice environment where logs can be aggregated (via ELK/Datadog) and traced linearly from User Input -> Orchestrator -> Transport -> Network Failure -> Retry -> Success.

## 5. Structured JSON Logging
**Decision:** Replace standard flat text logs with structured JSON formatting.
**Rationale:** Human-readable logs are useful for local debugging, but they are an anti-pattern in production environments. JSON logs allow logging aggregators to parse and index fields (`request_id`, `status_code`, `symbol`, `event`) out of the box, turning logs into queryable metrics.
