import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from bot.client import BinanceFuturesRESTClient
from bot.logging_config import logger
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_exchange_filters
)

# Load environment variables
load_dotenv()

def get_client() -> BinanceFuturesRESTClient:
    """Instantiates the BinanceFuturesRESTClient using credentials from the environment."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or api_key == "your_testnet_api_key_here":
        raise ValueError("BINANCE_API_KEY is not configured in .env file.")
    if not api_secret or api_secret == "your_testnet_api_secret_here":
        raise ValueError("BINANCE_API_SECRET is not configured in .env file.")
        
    return BinanceFuturesRESTClient(api_key, api_secret)

def execute_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None
) -> Dict[str, Any]:
    """Validates inputs, checks symbol existence defensively, and executes the order.
    
    Args:
        symbol: The trading symbol (e.g., BTCUSDT)
        side: BUY or SELL
        order_type: MARKET or LIMIT
        quantity: Qty to trade as a string
        price: Price as a string (required for LIMIT, STOP_LIMIT)
        stop_price: Stop price as a string (required for STOP_LIMIT)
        
    Returns:
        Dict: Response from the Binance Futures API
    """
    logger.info("Executing order orchestrator...")
    
    # 1. CLI Validation
    valid_symbol = validate_symbol(symbol)
    valid_side = validate_side(side)
    valid_type = validate_order_type(order_type)
    valid_qty = validate_quantity(quantity)
    
    is_limit_or_stop = (valid_type in ("LIMIT", "STOP_LIMIT"))
    valid_price = validate_price(price, required=is_limit_or_stop, field_name="Price")
    
    valid_stop_price = None
    if valid_type == "STOP_LIMIT":
        valid_stop_price = validate_price(stop_price, required=True, field_name="Stop Price")
    
    # 2. Get Client
    client = get_client()
    
    # 3. Defensive Programming: Verify Symbol exists via ExchangeInfo
    logger.info("Fetching exchange information to verify symbol existence...")
    exchange_info = client.get_exchange_info()
    symbols_in_exchange = {s["symbol"].upper(): s for s in exchange_info.get("symbols", [])}
    
    if valid_symbol not in symbols_in_exchange:
        error_msg = f"Invalid symbol: {valid_symbol}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    symbol_info = symbols_in_exchange[valid_symbol]
    
    # 4. Enforce Exchange Filters locally
    logger.info("Validating parameters against exchange rules...")
    validate_exchange_filters(symbol_info, valid_qty, valid_price)
    
    logger.info(f"Symbol {valid_symbol} verified successfully. Proceeding with order placement.")
    
    # 5. Place order
    result = client.place_order(
        symbol=valid_symbol,
        side=valid_side,
        order_type=valid_type,
        quantity=valid_qty,
        price=valid_price,
        stop_price=valid_stop_price
    )
    
    return result

def check_health() -> bool:
    """Checks the health of the Binance API and credentials."""
    try:
        client = get_client()
        server_time = client.get_server_time()
        logger.info(f"Server is healthy. Server time: {server_time}")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def get_order_status(symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
    """Queries the status of an existing order."""
    valid_symbol = validate_symbol(symbol)
    client = get_client()
    return client.query_order(valid_symbol, order_id, orig_client_order_id)

def cancel_existing_order(symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
    """Cancels an existing order."""
    valid_symbol = validate_symbol(symbol)
    client = get_client()
    return client.cancel_order(valid_symbol, order_id, orig_client_order_id)
