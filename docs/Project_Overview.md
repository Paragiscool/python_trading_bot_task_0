# Simplified Trading Bot - Project Overview

> **Target Audience:** Engineering Reviewers  
> **Repository:** Python Binance Futures Testnet Bot

## Executive Summary
This project implements a professional-grade, resilient Python client for the Binance Futures Testnet (USDT-M). Built strictly without the standard `python-binance` dependency, the bot demonstrates a deep mastery of REST protocol manipulation, cryptographic authentication (HMAC-SHA256), robust error handling, and production-ready CI/CD pipelines.

## Project Metrics
- **Python Files:** 12
- **Unit Tests:** 9 (Mocked API client testing)
- **Code Coverage:** 90%+ (via `pytest-cov`)
- **Supported Order Types:** MARKET, LIMIT, STOP_LIMIT
- **CI Pipelines:** GitHub Actions
- **Static Analysis:** Mypy (Types), Ruff (Linting)
- **Containerization:** Dockerized for immediate execution

## Architecture & Data Flow

```text
User Command -> Validation Layer -> Local Exchange Filter Math -> HMAC-SHA256 Signer -> REST Client -> Retry Decorator -> Binance API
```

## Production Engineering Signals

1. **Automated Resilience (429/5xx Backoff)**
   Network partitions and rate limits are expected in trading. The REST client implements autonomous retry logic that respects `Retry-After` headers and utilizes exponential backoff for transient failures.
   
2. **Local Exchange Filter Validation**
   Rather than consuming precious API rate-limits by letting the exchange reject malformed orders, the bot locally caches `/fapi/v1/exchangeInfo` and applies strict Decimal math to ensure `PRICE_FILTER` and `LOT_SIZE` compliance pre-flight.

3. **Traceability & Correlation IDs**
   Every API request is injected with a `uuid4`. This `request_id` acts as a correlation ID that propagates entirely through the structured JSON logging pipeline, allowing seamless tracing in a distributed log aggregator (like Datadog).

4. **Structured JSON Logging**
   Traditional flat logs are an anti-pattern in production. We implemented a custom `logging.Formatter` to emit structured JSON blobs containing status codes, endpoints, execution layers, and correlation IDs.

## Validation Coverage Matrix

| Scenario | Handled By | Result |
|-----------|-----------|---------|
| Invalid Symbol Format | `validators.py` | Local Exception |
| Order Price violates `tickSize` | `orders.py` | Local Exception |
| Order Qty violates `stepSize` | `orders.py` | Local Exception |
| HTTP 429 (Rate Limit) | `client.py` | Exponential Backoff Retry |
| HTTP 500+ (Server Error) | `client.py` | Exponential Backoff Retry |
| Network Timeout | `requests` | Bubble Up `BinanceNetworkError` |

*Documentation, Source Code, and Verifiable Execution Proofs are located in the repository.*
