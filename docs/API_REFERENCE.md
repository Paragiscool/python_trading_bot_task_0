# API Reference & CLI Commands

This document outlines the commands available via the `cli.py` interface.

## Global Options

- `-h`, `--help`: Show the help message and exit.

---

## 1. Interactive Menu
Starts a highly polished, guided interactive terminal session.
```bash
python cli.py interactive
```

---

## 2. Place Order (`place`)
Submits a new order to the Binance Futures Testnet.

### Arguments:
- `--symbol` (str, required): The trading pair (e.g., `BTCUSDT`).
- `--side` (str, required): `BUY` or `SELL`.
- `--type` (str, required): `MARKET`, `LIMIT`, or `STOP_LIMIT`.
- `--quantity` (float, required): Order quantity (must respect `stepSize`).
- `--price` (float, optional): Required for `LIMIT` and `STOP_LIMIT` orders.
- `--stop-price` (float, optional): Required for `STOP_LIMIT` orders.

### Examples:
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
python cli.py place --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 96000 --stop-price 95500
```

---

## 3. Order Status (`status`)
Retrieves the status of an active or historical order.

### Arguments:
- `--symbol` (str, required): The trading pair.
- `--order-id` (int, optional): The Binance order ID.
- `--orig-client-order-id` (str, optional): Your custom client order ID.
*(Note: At least one ID must be provided).*

### Example:
```bash
python cli.py status --symbol BTCUSDT --order-id 123456789
```

---

## 4. Cancel Order (`cancel`)
Cancels an active open order.

### Arguments:
- Same as `status`.

### Example:
```bash
python cli.py cancel --symbol BTCUSDT --order-id 123456789
```

---

## 5. Account Information (`account`)
Retrieves your aggregate wallet, available, and margin balances.
```bash
python cli.py account
```

---

## 6. Open Orders (`open-orders`)
Retrieves a list of all currently open orders.
```bash
python cli.py open-orders
python cli.py open-orders --symbol BTCUSDT
```

---

## 7. Active Positions (`positions`)
Retrieves a list of all positions where the position amount is non-zero.
```bash
python cli.py positions
python cli.py positions --symbol BTCUSDT
```

---

## 8. Health Check (`health`)
Verifies API connectivity, credentials validity, and network latency.
```bash
python cli.py health
```
