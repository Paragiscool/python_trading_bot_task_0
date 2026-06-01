import pytest
from unittest.mock import patch, MagicMock
from bot.orders import execute_order

@pytest.fixture
def mock_client(mocker):
    client_mock = MagicMock()
    client_mock.get_exchange_info.return_value = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "filters": [
                    {"filterType": "PRICE_FILTER", "minPrice": "0.10", "maxPrice": "100000.00", "tickSize": "0.10"},
                    {"filterType": "LOT_SIZE", "minQty": "0.001", "maxQty": "1000.000", "stepSize": "0.001"},
                    {"filterType": "MIN_NOTIONAL", "notional": "5.0"}
                ]
            }
        ]
    }
    client_mock.place_order.return_value = {"orderId": 12345, "status": "NEW"}
    
    mocker.patch("bot.orders.get_client", return_value=client_mock)
    return client_mock

def test_execute_order_valid(mock_client):
    response = execute_order(
        symbol="BTCUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity="0.001",
        price="95000.0"
    )
    
    assert response["orderId"] == 12345
    mock_client.place_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=0.001,
        price=95000.0,
        stop_price=None
    )

def test_execute_order_invalid_symbol(mock_client):
    with pytest.raises(ValueError, match="Invalid symbol: ETHUSDT"):
        execute_order(
            symbol="ETHUSDT",
            side="BUY",
            order_type="MARKET",
            quantity="0.001"
        )
