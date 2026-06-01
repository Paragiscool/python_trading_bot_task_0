import re
from typing import Optional

def validate_symbol(symbol: str) -> str:
    """Validates basic format of the trading symbol."""
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    
    clean_symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z0-9]{3,12}$", clean_symbol):
        raise ValueError(
            f"Invalid symbol format: '{symbol}'. Must be 3-12 alphanumeric uppercase characters."
        )
    return clean_symbol

def validate_side(side: str) -> str:
    """Validates the order side (BUY or SELL)."""
    clean_side = side.strip().upper()
    if clean_side not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side: '{side}'. Must be 'BUY' or 'SELL'.")
    return clean_side

def validate_order_type(order_type: str) -> str:
    """Validates the order type (MARKET or LIMIT)."""
    clean_type = order_type.strip().upper()
    if clean_type not in ("MARKET", "LIMIT"):
        raise ValueError(f"Invalid order type: '{order_type}'. Must be 'MARKET' or 'LIMIT'.")
    return clean_type

def validate_quantity(quantity: str) -> float:
    """Validates that the quantity is a positive float."""
    try:
        qty_val = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity: '{quantity}'. Must be a number.")
    
    if qty_val <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty_val}")
    return qty_val

def validate_price(price: Optional[str], required: bool = False) -> Optional[float]:
    """Validates price parameter. Required for LIMIT orders."""
    if price is None or price.strip() == "":
        if required:
            raise ValueError("Price is required for LIMIT orders.")
        return None
    
    try:
        price_val = float(price)
    except ValueError:
        raise ValueError(f"Invalid price: '{price}'. Must be a number.")
    
    if price_val <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {price_val}")
    return price_val
