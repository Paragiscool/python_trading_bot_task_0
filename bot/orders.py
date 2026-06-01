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
    validate_price
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
    price: Optional[str] = None
) -> Dict[str, Any]:
    """Validates inputs, checks symbol existence defensively, and executes the order.
    
    Args:
        symbol: The trading symbol (e.g., BTCUSDT)
        side: BUY or SELL
        order_type: MARKET or LIMIT
        quantity: Qty to trade as a string
        price: Price as a string (required for LIMIT)
        
    Returns:
        Dict: Response from the Binance Futures API
    """
    logger.info("Executing order orchestrator...")
    
    # 1. CLI Validation
    valid_symbol = validate_symbol(symbol)
    valid_side = validate_side(side)
    valid_type = validate_order_type(order_type)
    valid_qty = validate_quantity(quantity)
    
    is_limit = (valid_type == "LIMIT")
    valid_price = validate_price(price, required=is_limit)
    
    # 2. Get Client
    client = get_client()
    
    # 3. Defensive Programming: Verify Symbol exists via ExchangeInfo
    logger.info("Fetching exchange information to verify symbol existence...")
    exchange_info = client.get_exchange_info()
    symbols_in_exchange = {s["symbol"].upper() for s in exchange_info.get("symbols", [])}
    
    if valid_symbol not in symbols_in_exchange:
        error_msg = f"Invalid symbol: {valid_symbol}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    logger.info(f"Symbol {valid_symbol} verified successfully. Proceeding with order placement.")
    
    # 4. Place order
    result = client.place_order(
        symbol=valid_symbol,
        side=valid_side,
        order_type=valid_type,
        quantity=valid_qty,
        price=valid_price
    )
    
    return result
