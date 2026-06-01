import re
from typing import Optional, Dict, Any
from decimal import Decimal

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
    """Validates the order type (MARKET, LIMIT, or STOP_LIMIT)."""
    clean_type = order_type.strip().upper()
    if clean_type not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValueError(f"Invalid order type: '{order_type}'. Must be 'MARKET', 'LIMIT', or 'STOP_LIMIT'.")
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

def validate_price(price: Optional[str], required: bool = False, field_name: str = "Price") -> Optional[float]:
    """Validates price parameter. Required for LIMIT and STOP_LIMIT orders."""
    if price is None or price.strip() == "":
        if required:
            raise ValueError(f"{field_name} is required for this order type.")
        return None
    
    try:
        price_val = float(price)
    except ValueError:
        raise ValueError(f"Invalid price: '{price}'. Must be a number.")
    
    if price_val <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {price_val}")
    return price_val

def validate_exchange_filters(symbol_info: Dict[str, Any], quantity: float, price: Optional[float] = None) -> None:
    """Validates order against exchange rules for LOT_SIZE, PRICE_FILTER, and MIN_NOTIONAL."""
    filters = {f["filterType"]: f for f in symbol_info.get("filters", [])}
    
    # Lot Size Validation
    lot_size = filters.get("LOT_SIZE")
    if lot_size:
        min_qty = float(lot_size["minQty"])
        max_qty = float(lot_size["maxQty"])
        step_size = lot_size["stepSize"]
        
        if quantity < min_qty or quantity > max_qty:
            raise ValueError(f"Quantity {quantity} must be between {min_qty} and {max_qty}")
            
        qty_dec = Decimal(str(quantity))
        step_dec = Decimal(str(step_size))
        if qty_dec % step_dec != 0:
            raise ValueError(f"Quantity {quantity} must be a multiple of {step_size}")

    # Price Filter Validation
    if price is not None:
        price_filter = filters.get("PRICE_FILTER")
        if price_filter:
            min_price = float(price_filter["minPrice"])
            max_price = float(price_filter["maxPrice"])
            tick_size = price_filter["tickSize"]
            
            if price < min_price or price > max_price:
                raise ValueError(f"Price {price} must be between {min_price} and {max_price}")
                
            price_dec = Decimal(str(price))
            tick_dec = Decimal(str(tick_size))
            if price_dec % tick_dec != 0:
                raise ValueError(f"Price {price} must be a multiple of {tick_size}")
                
        # Min Notional Validation
        min_notional_filter = filters.get("MIN_NOTIONAL")
        if min_notional_filter:
            notional = float(min_notional_filter.get("notional", 0))
            if quantity * price < notional:
                raise ValueError(f"Order notional value (quantity * price) must be >= {notional}")

