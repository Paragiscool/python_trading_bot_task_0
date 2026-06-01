import pytest
import requests
from unittest.mock import patch, MagicMock
from bot.client import BinanceFuturesRESTClient, BinanceAPIError, BinanceNetworkError

def test_api_error_handling():
    client = BinanceFuturesRESTClient("api", "secret")
    
    with patch("requests.request") as mock_request:
        # Mocking an API error response (e.g., Invalid API Key)
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"code": -2015, "msg": "Invalid API-key, IP, or permissions for action."}
        mock_request.return_value = mock_resp
        
        with pytest.raises(BinanceAPIError) as excinfo:
            client.get_server_time()
            
        assert excinfo.value.code == -2015
        assert excinfo.value.status_code == 401
        assert "Invalid API-key" in str(excinfo.value)

def test_network_error_handling():
    client = BinanceFuturesRESTClient("api", "secret")
    
    with patch("requests.request", side_effect=requests.exceptions.Timeout("Connection timed out")):
        with pytest.raises(BinanceNetworkError, match="Connection timed out"):
            client.get_server_time()
