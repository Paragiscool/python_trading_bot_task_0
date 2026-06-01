# Validation & Error Handling Matrix

A resilient trading system must anticipate failure at every boundary. This document outlines exactly how the `Simplified Trading Bot` handles malformed inputs, API limits, and network volatility.

## Validation Coverage

| Scenario | Handled By | Result |
|-----------|-----------|---------|
| Invalid Symbol Format | `validators.py` | Local Exception (`ValueError`) |
| Order Price violates `tickSize` | `orders.py` | Local Exception (`ValueError`) |
| Order Qty violates `stepSize` | `orders.py` | Local Exception (`ValueError`) |
| HTTP 429 (Rate Limit) | `client.py` | Exponential Backoff Retry (Auto-throttle) |
| HTTP 500+ (Server Error) | `client.py` | Exponential Backoff Retry |
| Network Timeout | `requests` | Bubble Up `BinanceNetworkError` |
| Invalid API Key | `client.py` | Fail Fast `BinanceAPIError` (No retries on 401) |

## Pre-Flight Exchange Filter Rules

Instead of forwarding a malformed request to Binance (which counts against rate-limits and IP reputation), the bot proactively enforces Binance's `PRICE_FILTER` and `LOT_SIZE` locally:

1. **`tickSize` validation**: Limits order prices to valid increments (e.g., Bitcoin step size of `0.10`).
2. **`stepSize` validation**: Limits order quantities to valid lot sizes.
3. **Decimals strictness**: Ensures that floats do not suffer from IEEE floating-point imprecision when constructing payloads.

*For implementation details, refer to `bot/validators.py` and `bot/orders.py`.*
