import pytest
from bot.validators import validate_exchange_filters

@pytest.fixture
def mock_exchange_info():
    return {
        "symbol": "BTCUSDT",
        "filters": [
            {
                "filterType": "PRICE_FILTER",
                "minPrice": "0.10",
                "maxPrice": "100000.00",
                "tickSize": "0.10"
            },
            {
                "filterType": "LOT_SIZE",
                "minQty": "0.001",
                "maxQty": "1000.000",
                "stepSize": "0.001"
            },
            {
                "filterType": "MIN_NOTIONAL",
                "notional": "5.0"
            }
        ]
    }

def test_validate_exchange_filters_valid(mock_exchange_info):
    # Valid MARKET order (no price)
    validate_exchange_filters(mock_exchange_info, quantity=0.005)
    
    # Valid LIMIT order
    validate_exchange_filters(mock_exchange_info, quantity=0.005, price=95000.1)

def test_validate_exchange_filters_invalid_lot_size(mock_exchange_info):
    with pytest.raises(ValueError, match="must be between"):
        validate_exchange_filters(mock_exchange_info, quantity=0.0001)  # below minQty
        
    with pytest.raises(ValueError, match="must be a multiple of"):
        validate_exchange_filters(mock_exchange_info, quantity=0.0015)  # invalid stepSize

def test_validate_exchange_filters_invalid_price(mock_exchange_info):
    with pytest.raises(ValueError, match="must be between"):
        validate_exchange_filters(mock_exchange_info, quantity=0.001, price=0.05)  # below minPrice
        
    with pytest.raises(ValueError, match="must be a multiple of"):
        validate_exchange_filters(mock_exchange_info, quantity=0.001, price=95000.15)  # invalid tickSize

def test_validate_exchange_filters_invalid_notional(mock_exchange_info):
    with pytest.raises(ValueError, match="must be >="):
        validate_exchange_filters(mock_exchange_info, quantity=0.001, price=4000.0)  # 0.001 * 4000 = 4.0 < 5.0
