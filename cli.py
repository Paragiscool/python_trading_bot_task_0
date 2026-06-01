import argparse
import sys
from typing import Optional

from bot.orders import execute_order
from bot.logging_config import logger

def main():
    parser = argparse.ArgumentParser(
        description="A Simplified Trading Bot for Binance Futures Testnet (USDT-M)"
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side (BUY or SELL)")
    parser.add_argument("--type", required=True, choices=["MARKET", "LIMIT"], help="Order type (MARKET or LIMIT)")
    parser.add_argument("--quantity", required=True, help="Quantity to trade")
    parser.add_argument("--price", required=False, default=None, help="Limit price (required if type is LIMIT)")

    args = parser.parse_args()

    # Print Request Summary
    print("========================================")
    print("         ORDER REQUEST SUMMARY          ")
    print("========================================")
    print(f"Symbol:    {args.symbol.upper()}")
    print(f"Side:      {args.side.upper()}")
    print(f"Type:      {args.type.upper()}")
    print(f"Quantity:  {args.quantity}")
    print(f"Price:     {args.price if args.price else 'N/A'}")
    print("========================================")
    print("Sending order request...")

    try:
        response = execute_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price
        )
        
        # Display Success Message
        print("\n[SUCCESS] Order placed successfully!")
        print("----------------------------------------")
        print("         ORDER RESPONSE DETAILS         ")
        print("----------------------------------------")
        print(f"Order ID:      {response.get('orderId')}")
        print(f"Status:        {response.get('status')}")
        print(f"Executed Qty:  {response.get('executedQty')}")
        
        # avgPrice is returned in USDT-M Futures order responses. If 0, display 'N/A / Pending'
        avg_price = response.get("avgPrice", "0.0")
        try:
            avg_price_val = float(avg_price)
            if avg_price_val == 0.0:
                # If avgPrice is 0, show standard price or limit price representation
                price_val = response.get("price", "0.0")
                if float(price_val) > 0.0:
                    avg_price_display = f"{price_val} (Limit Price)"
                else:
                    avg_price_display = "N/A (Pending Execution)"
            else:
                avg_price_display = f"{avg_price_val:.2f}"
        except (ValueError, TypeError):
            avg_price_display = avg_price
            
        print(f"Avg Price:     {avg_price_display}")
        print("----------------------------------------")
        
    except Exception as e:
        print(f"\n[FAILURE] Order execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
