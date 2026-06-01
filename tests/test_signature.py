import pytest
from bot.client import BinanceFuturesRESTClient

def test_generate_signature():
    client = BinanceFuturesRESTClient("api_key", "secret_key")
    query_string = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=1700000000000"
    
    # Expected signature can be calculated via external tool or verified against a known test case
    # This is an example HMAC SHA256 of the above string using 'secret_key'
    import hashlib
    import hmac
    expected = hmac.new(b"secret_key", query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    
    sig = client._generate_signature(query_string)
    assert sig == expected
