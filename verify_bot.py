import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.orders import execute_order
from bot.logging_config import logger

class TestTradingBotREST(unittest.TestCase):

    @patch('bot.orders.os.getenv')
    @patch('bot.client.requests.request')
    def test_market_order_success(self, mock_requests, mock_getenv):
        """Mocks and tests a successful MARKET order placement."""
        # Setup env credentials mock
        mock_getenv.side_effect = lambda key, default=None: {
            "BINANCE_API_KEY": "mock_api_key",
            "BINANCE_API_SECRET": "mock_api_secret"
        }.get(key, default)

        # Mock ExchangeInfo response and Order response
        mock_exchange_info = MagicMock()
        mock_exchange_info.status_code = 200
        mock_exchange_info.ok = True
        mock_exchange_info.json.return_value = {
            "symbols": [
                {"symbol": "BTCUSDT"}
            ]
        }

        mock_order_response = MagicMock()
        mock_order_response.status_code = 200
        mock_order_response.ok = True
        mock_order_response.json.return_value = {
            "orderId": 11112222,
            "symbol": "BTCUSDT",
            "status": "NEW",
            "clientOrderId": "mock_client_order_id",
            "side": "BUY",
            "type": "MARKET",
            "origQty": "0.005",
            "executedQty": "0.005",
            "avgPrice": "62000.50",
            "price": "0.00",
            "updateTime": 1717228800000
        }

        # First request is for exchangeInfo (GET), second is for order (POST)
        mock_requests.side_effect = [mock_exchange_info, mock_order_response]

        print("\n--- Running Mocked MARKET Order Test ---")
        result = execute_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity="0.005"
        )

        self.assertEqual(result["orderId"], 11112222)
        self.assertEqual(result["executedQty"], "0.005")
        self.assertEqual(result["status"], "NEW")
        print("Mocked MARKET Order success verified.")

    @patch('bot.orders.os.getenv')
    @patch('bot.client.requests.request')
    def test_limit_order_success(self, mock_requests, mock_getenv):
        """Mocks and tests a successful LIMIT order placement."""
        # Setup env credentials mock
        mock_getenv.side_effect = lambda key, default=None: {
            "BINANCE_API_KEY": "mock_api_key",
            "BINANCE_API_SECRET": "mock_api_secret"
        }.get(key, default)

        # Mock ExchangeInfo response and Order response
        mock_exchange_info = MagicMock()
        mock_exchange_info.status_code = 200
        mock_exchange_info.ok = True
        mock_exchange_info.json.return_value = {
            "symbols": [
                {"symbol": "BTCUSDT"}
            ]
        }

        mock_order_response = MagicMock()
        mock_order_response.status_code = 200
        mock_order_response.ok = True
        mock_order_response.json.return_value = {
            "orderId": 33334444,
            "symbol": "BTCUSDT",
            "status": "NEW",
            "clientOrderId": "mock_limit_order_id",
            "side": "SELL",
            "type": "LIMIT",
            "origQty": "0.010",
            "executedQty": "0.000",
            "avgPrice": "0.00",
            "price": "65000.00",
            "updateTime": 1717228900000
        }

        # First request is for exchangeInfo (GET), second is for order (POST)
        mock_requests.side_effect = [mock_exchange_info, mock_order_response]

        print("\n--- Running Mocked LIMIT Order Test ---")
        result = execute_order(
            symbol="BTCUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity="0.010",
            price="65000"
        )

        self.assertEqual(result["orderId"], 33334444)
        self.assertEqual(result["price"], "65000.00")
        print("Mocked LIMIT Order success verified.")

    @patch('bot.orders.os.getenv')
    @patch('bot.client.requests.request')
    def test_invalid_symbol_defensive_programming(self, mock_requests, mock_getenv):
        """Tests that checking invalid symbols defensively raises a ValueError before placing an order."""
        # Setup env credentials mock
        mock_getenv.side_effect = lambda key, default=None: {
            "BINANCE_API_KEY": "mock_api_key",
            "BINANCE_API_SECRET": "mock_api_secret"
        }.get(key, default)

        # Mock ExchangeInfo response
        mock_exchange_info = MagicMock()
        mock_exchange_info.status_code = 200
        mock_exchange_info.ok = True
        mock_exchange_info.json.return_value = {
            "symbols": [
                {"symbol": "BTCUSDT"}
            ]
        }

        mock_requests.return_value = mock_exchange_info

        print("\n--- Running Mocked Invalid Symbol Check Test ---")
        with self.assertRaises(ValueError) as context:
            execute_order(
                symbol="ABCXYZ",
                side="BUY",
                order_type="MARKET",
                quantity="0.001"
            )
        
        self.assertIn("Invalid symbol: ABCXYZ", str(context.exception))
        # Ensure request to order was never made because error was raised in orchestrator
        self.assertEqual(mock_requests.call_count, 1) # Only exchangeInfo request
        print("Defensive programming verification passed (Invalid symbol rejected).")

if __name__ == '__main__':
    unittest.main()
