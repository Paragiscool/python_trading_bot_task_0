import hashlib
import hmac
import time
import os
import requests
from urllib.parse import urlencode
from typing import Dict, Any, Optional
from bot.logging_config import logger

class BinanceAPIError(Exception):
    """Exception raised for errors returned by the Binance API."""
    def __init__(self, code: int, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"Binance API Error: [Code {code}] {message} (HTTP {status_code})")

class BinanceNetworkError(Exception):
    """Exception raised for connection or network failures."""
    pass

class BinanceFuturesRESTClient:
    """A direct REST API client for Binance Futures Testnet (USDT-M)."""

    def __init__(self, api_key: str, api_secret: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Default to testnet website base URL but support custom override if necessary
        self.base_url = (base_url or os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")).rstrip("/")
        
        self.headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        logger.info(f"Initialized Binance Futures REST Client on base URL: {self.base_url}")

    def _generate_signature(self, query_string: str) -> str:
        """Generates HMAC-SHA256 signature for signed requests."""
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def _send_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False) -> Dict[str, Any]:
        """Formats, signs (if required), and sends an HTTP request to the Binance REST API."""
        params = params or {}
        url = f"{self.base_url}{endpoint}"

        # Setup logging metadata
        logger.info(f"Preparing {method} request to endpoint: {endpoint}")
        
        if signed:
            # Add current millisecond timestamp
            params["timestamp"] = int(time.time() * 1000)
            # URL-encode the parameters query string
            query_string = urlencode(params)
            # Generate the hmac signature on the query string
            sig = self._generate_signature(query_string)
            # Append signature
            url_with_params = f"{url}?{query_string}&signature={sig}"
            logged_url = f"{url}?{query_string}&signature=[REDACTED]"
        else:
            if params:
                query_string = urlencode(params)
                url_with_params = f"{url}?{query_string}"
                logged_url = url_with_params
            else:
                url_with_params = url
                logged_url = url

        logger.debug(f"Request URL: {logged_url} (API Key headers loaded)")

        try:
            response = requests.request(method, url_with_params, headers=self.headers, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending request: {str(e)}")
            raise BinanceNetworkError(f"Network connection failed: {str(e)}")

        # Log status code and raw response
        logger.info(f"Received response: HTTP {response.status_code}")
        logger.debug(f"Raw Response Body: {response.text}")

        # Parse response
        try:
            res_data = response.json()
        except ValueError:
            logger.error("Failed to parse response body as JSON.")
            raise BinanceNetworkError("Invalid response format received from server (not JSON).")

        if not response.ok:
            code = res_data.get("code", -1)
            msg = res_data.get("msg", "Unknown error")
            logger.error(f"Binance API rejected request: Code {code} - {msg}")
            raise BinanceAPIError(code=code, message=msg, status_code=response.status_code)

        return res_data

    def get_server_time(self) -> int:
        """Fetches the current server time in milliseconds."""
        res = self._send_request("GET", "/fapi/v1/time")
        return res["serverTime"]

    def get_exchange_info(self) -> Dict[str, Any]:
        """Fetches exchange information (metadata about rules and symbols)."""
        return self._send_request("GET", "/fapi/v1/exchangeInfo")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Places an order (MARKET or LIMIT) on Binance Futures Testnet (USDT-M)."""
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }

        if order_type.upper() == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        logger.info(f"Placing signed order request: {params}")
        return self._send_request("POST", "/fapi/v1/order", params=params, signed=True)
