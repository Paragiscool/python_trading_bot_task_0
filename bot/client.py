import hashlib
import hmac
import time
import os
import uuid
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
        env_url = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")
        # Ensure it's treated strictly as a string
        url_str: str = base_url if base_url is not None else (env_url if env_url is not None else "https://testnet.binancefuture.com")
        self.base_url = url_str.rstrip("/")
        
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

    def _send_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False, max_retries: int = 3) -> Any:
        """Formats, signs (if required), and sends an HTTP request to the Binance REST API with retry backoff."""
        params = params or {}
        req_id = str(uuid.uuid4())
        
        for attempt in range(1, max_retries + 1):
            url = f"{self.base_url}{endpoint}"

            # Setup logging metadata
            logger.info(f"Preparing {method} request to endpoint: {endpoint}", extra={"request_id": req_id})
            
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

            logger.debug(f"Request URL: {logged_url} (API Key headers loaded)", extra={"request_id": req_id})

            try:
                response = requests.request(method, url_with_params, headers=self.headers, timeout=10)
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error sending request: {str(e)}", extra={"request_id": req_id})
                if attempt == max_retries:
                    raise BinanceNetworkError(f"Network connection failed: {str(e)}")
                time.sleep(2 ** attempt)
                continue

            # Log status code and raw response
            logger.info(f"Received response: HTTP {response.status_code}", extra={"request_id": req_id})
            
            if response.status_code == 429 or response.status_code >= 500:
                retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                logger.warning(f"Rate limited or server error (HTTP {response.status_code}). Retrying in {retry_after}s...", extra={"request_id": req_id})
                if attempt == max_retries:
                    raise BinanceAPIError(code=response.status_code, message="Max retries exceeded", status_code=response.status_code)
                time.sleep(retry_after)
                continue

            logger.debug(f"Raw Response Body: {response.text}", extra={"request_id": req_id})

            # Parse response
            try:
                res_data = response.json()
            except ValueError:
                logger.error("Failed to parse response body as JSON.", extra={"request_id": req_id})
                raise BinanceNetworkError("Invalid response format received from server (not JSON).")

            if not response.ok:
                code = res_data.get("code", -1)
                msg = res_data.get("msg", "Unknown error")
                logger.error(f"Binance API rejected request: Code {code} - {msg}", extra={"request_id": req_id})
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
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Places an order (MARKET, LIMIT, or STOP_LIMIT) on Binance Futures Testnet (USDT-M)."""
        # Map STOP_LIMIT to Binance API's 'STOP' order type
        api_order_type = "STOP" if order_type.upper() == "STOP_LIMIT" else order_type.upper()
        
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": api_order_type,
            "quantity": quantity
        }

        if api_order_type in ("LIMIT", "STOP"):
            if price is None:
                raise ValueError("Price is required for LIMIT and STOP orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force
            
        if api_order_type == "STOP":
            if stop_price is None:
                raise ValueError("Stop price is required for STOP orders.")
            params["stopPrice"] = stop_price

        logger.info(f"Placing signed order request: {params}")
        return self._send_request("POST", "/fapi/v1/order", params=params, signed=True)

    def query_order(self, symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Queries the status of an existing order."""
        if not order_id and not orig_client_order_id:
            raise ValueError("Either order_id or orig_client_order_id must be provided.")
        
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
            
        return self._send_request("GET", "/fapi/v1/order", params=params, signed=True)

    def cancel_order(self, symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """Cancels an existing order."""
        if not order_id and not orig_client_order_id:
            raise ValueError("Either order_id or orig_client_order_id must be provided.")
            
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
            
        return self._send_request("DELETE", "/fapi/v1/order", params=params, signed=True)

    def get_account_info(self) -> Dict[str, Any]:
        """Fetches account information including balances."""
        return self._send_request("GET", "/fapi/v2/account", signed=True)

    def get_open_orders(self, symbol: Optional[str] = None) -> Any:
        """Fetches open orders. If symbol is provided, fetches only for that symbol."""
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._send_request("GET", "/fapi/v1/openOrders", params=params, signed=True)

    def get_positions(self, symbol: Optional[str] = None) -> Any:
        """Fetches position information."""
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._send_request("GET", "/fapi/v2/positionRisk", params=params, signed=True)
