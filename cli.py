import argparse
import sys
from typing import Optional

from bot.orders import execute_order, check_health, get_order_status, cancel_existing_order
from bot.logging_config import logger

def print_separator():
    print("-" * 40)

def print_header(title):
    print("=" * 40)
    print(f" {title:^38} ")
    print("=" * 40)

def handle_place(args):
    print_header("ORDER REQUEST SUMMARY")
    print(f"Symbol:      {args.symbol.upper()}")
    print(f"Side:        {args.side.upper()}")
    print(f"Type:        {args.type.upper()}")
    print(f"Quantity:    {args.quantity}")
    if args.type in ("LIMIT", "STOP_LIMIT"):
        print(f"Price:       {args.price if args.price else 'N/A'}")
    if args.type == "STOP_LIMIT":
        print(f"Stop Price:  {args.stop_price if args.stop_price else 'N/A'}")
    print_header("Sending order request...")

    try:
        response = execute_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price
        )
        
        print("\n[SUCCESS] Order placed successfully!")
        print_separator()
        print("         ORDER RESPONSE DETAILS         ")
        print_separator()
        print(f"Order ID:      {response.get('orderId')}")
        print(f"Status:        {response.get('status')}")
        print(f"Executed Qty:  {response.get('executedQty')}")
        
        avg_price = response.get("avgPrice", "0.0")
        try:
            if float(avg_price) == 0.0:
                price_val = response.get("price", "0.0")
                if float(price_val) > 0.0:
                    avg_price_display = f"{price_val} (Limit Price)"
                else:
                    avg_price_display = "N/A (Pending Execution)"
            else:
                avg_price_display = f"{float(avg_price):.2f}"
        except ValueError:
            avg_price_display = avg_price
            
        print(f"Avg Price:     {avg_price_display}")
        print_separator()
        
    except Exception as e:
        print(f"\n[FAILURE] Order execution failed: {str(e)}")
        sys.exit(1)

def handle_health(args):
    print_header("HEALTH CHECK")
    if check_health():
        print("[SUCCESS] Connected to Binance Futures Testnet successfully!")
    else:
        print("[FAILURE] Could not connect or authenticate.")
        sys.exit(1)

def handle_status(args):
    print_header("ORDER STATUS")
    try:
        response = get_order_status(args.symbol, args.order_id, args.orig_client_order_id)
        print(f"Order ID:      {response.get('orderId')}")
        print(f"Status:        {response.get('status')}")
        print(f"Type:          {response.get('type')}")
        print(f"Side:          {response.get('side')}")
        print(f"Orig Qty:      {response.get('origQty')}")
        print(f"Executed Qty:  {response.get('executedQty')}")
        print_separator()
    except Exception as e:
        print(f"\n[FAILURE] Status query failed: {str(e)}")
        sys.exit(1)

def handle_cancel(args):
    print_header("CANCEL ORDER")
    try:
        response = cancel_existing_order(args.symbol, args.order_id, args.orig_client_order_id)
        print("\n[SUCCESS] Order cancelled successfully!")
        print(f"Order ID:      {response.get('orderId')}")
        print(f"Status:        {response.get('status')}")
        print_separator()
    except Exception as e:
        print(f"\n[FAILURE] Cancel failed: {str(e)}")
        sys.exit(1)

def interactive_menu():
    print_header("INTERACTIVE TRADING BOT")
    while True:
        print("\nWhat would you like to do?")
        print("1. Place Order")
        print("2. Check Order Status")
        print("3. Cancel Order")
        print("4. Check API Health")
        print("5. Exit")
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            symbol = input("Symbol (e.g. BTCUSDT): ").strip()
            side = input("Side (BUY/SELL): ").strip().upper()
            o_type = input("Order Type (MARKET/LIMIT/STOP_LIMIT): ").strip().upper()
            qty = input("Quantity: ").strip()
            
            price = None
            stop_price = None
            if o_type in ("LIMIT", "STOP_LIMIT"):
                price = input("Price: ").strip()
            if o_type == "STOP_LIMIT":
                stop_price = input("Stop Price: ").strip()
                
            class Args: pass
            args = Args()
            args.symbol = symbol; args.side = side; args.type = o_type; args.quantity = qty
            args.price = price; args.stop_price = stop_price
            handle_place(args)
            
        elif choice == '2':
            symbol = input("Symbol: ").strip()
            oid = input("Order ID (leave blank if none): ").strip()
            coid = input("Client Order ID (leave blank if none): ").strip()
            class Args: pass
            args = Args()
            args.symbol = symbol
            args.order_id = int(oid) if oid else None
            args.orig_client_order_id = coid if coid else None
            handle_status(args)
            
        elif choice == '3':
            symbol = input("Symbol: ").strip()
            oid = input("Order ID (leave blank if none): ").strip()
            coid = input("Client Order ID (leave blank if none): ").strip()
            class Args: pass
            args = Args()
            args.symbol = symbol
            args.order_id = int(oid) if oid else None
            args.orig_client_order_id = coid if coid else None
            handle_cancel(args)
            
        elif choice == '4':
            class Args: pass
            handle_health(Args())
            
        elif choice == '5':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

def main():
    parser = argparse.ArgumentParser(
        description="A Simplified Trading Bot for Binance Futures Testnet (USDT-M)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Place command
    place_parser = subparsers.add_parser("place", help="Place a new order")
    place_parser.add_argument("--symbol", required=True, help="Trading symbol (e.g. BTCUSDT)")
    place_parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side (BUY or SELL)")
    place_parser.add_argument("--type", required=True, choices=["MARKET", "LIMIT", "STOP_LIMIT"], help="Order type")
    place_parser.add_argument("--quantity", required=True, help="Quantity to trade")
    place_parser.add_argument("--price", required=False, default=None, help="Limit price (required if type is LIMIT or STOP_LIMIT)")
    place_parser.add_argument("--stop-price", required=False, default=None, help="Stop price (required if type is STOP_LIMIT)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check order status")
    status_parser.add_argument("--symbol", required=True, help="Trading symbol")
    status_parser.add_argument("--order-id", type=int, default=None, help="Binance Order ID")
    status_parser.add_argument("--orig-client-order-id", default=None, help="Client Order ID")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an order")
    cancel_parser.add_argument("--symbol", required=True, help="Trading symbol")
    cancel_parser.add_argument("--order-id", type=int, default=None, help="Binance Order ID")
    cancel_parser.add_argument("--orig-client-order-id", default=None, help="Client Order ID")
    
    # Health command
    subparsers.add_parser("health", help="Check API health and credentials")
    
    # Interactive command
    subparsers.add_parser("interactive", help="Start the interactive menu")

    args = parser.parse_args()

    if args.command == "place":
        handle_place(args)
    elif args.command == "status":
        handle_status(args)
    elif args.command == "cancel":
        handle_cancel(args)
    elif args.command == "health":
        handle_health(args)
    elif args.command == "interactive":
        interactive_menu()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
