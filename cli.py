import argparse
import sys
from argparse import Namespace

from bot.orders import execute_order, check_health, get_order_status, cancel_existing_order, get_wallet_balance, get_active_orders, get_active_positions

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

def handle_account(args):
    print_header("ACCOUNT INFO")
    try:
        b = get_wallet_balance()
        print(f"Wallet Balance:      {b.get('wallet_balance')}")
        print(f"Available Balance:   {b.get('available_balance')}")
        print(f"Unrealized PnL:      {b.get('unrealized_pnl')}")
        print(f"Margin Balance:      {b.get('margin_balance')}")
        print_separator()
    except Exception as e:
        print(f"\n[FAILURE] Failed to fetch account info: {str(e)}")
        sys.exit(1)

def handle_open_orders(args):
    print_header("OPEN ORDERS")
    try:
        orders = get_active_orders(args.symbol)
        if not orders:
            print("No open orders found.")
        else:
            for o in orders:
                print(f"Symbol: {o.get('symbol')} | OrderID: {o.get('orderId')} | Side: {o.get('side')} | Type: {o.get('type')} | Price: {o.get('price')} | OrigQty: {o.get('origQty')}")
        print_separator()
    except Exception as e:
        print(f"\n[FAILURE] Failed to fetch open orders: {str(e)}")
        sys.exit(1)

def handle_positions(args):
    print_header("ACTIVE POSITIONS")
    try:
        positions = get_active_positions(args.symbol)
        if not positions:
            print("No active positions found.")
        else:
            for p in positions:
                print(f"Symbol: {p.get('symbol')} | PositionAmt: {p.get('positionAmt')} | EntryPrice: {p.get('entryPrice')} | unRealizedProfit: {p.get('unRealizedProfit')}")
        print_separator()
    except Exception as e:
        print(f"\n[FAILURE] Failed to fetch positions: {str(e)}")
        sys.exit(1)

def interactive_menu():
    print_header("INTERACTIVE TRADING BOT")
    while True:
        print("\nWhat would you like to do?")
        print("1. Place Order")
        print("2. Check Order Status")
        print("3. Cancel Order")
        print("4. Check Account Info")
        print("5. Check Open Orders")
        print("6. Check Active Positions")
        print("7. Check API Health")
        print("8. Exit")
        choice = input("\nEnter choice (1-8): ").strip()
        
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
                
            args = Namespace(symbol=symbol, side=side, type=o_type, quantity=qty, price=price, stop_price=stop_price)
            handle_place(args)
            
        elif choice == '2':
            symbol = input("Symbol: ").strip()
            oid = input("Order ID (leave blank if none): ").strip()
            coid = input("Client Order ID (leave blank if none): ").strip()
            args = Namespace(
                symbol=symbol,
                order_id=int(oid) if oid else None,
                orig_client_order_id=coid if coid else None
            )
            handle_status(args)
            
        elif choice == '3':
            symbol = input("Symbol: ").strip()
            oid = input("Order ID (leave blank if none): ").strip()
            coid = input("Client Order ID (leave blank if none): ").strip()
            args = Namespace(
                symbol=symbol,
                order_id=int(oid) if oid else None,
                orig_client_order_id=coid if coid else None
            )
            handle_cancel(args)
            
        elif choice == '4':
            handle_account(Namespace())
            
        elif choice == '5':
            symbol = input("Symbol (leave blank for all): ").strip()
            args = Namespace(symbol=symbol if symbol else None)
            handle_open_orders(args)
            
        elif choice == '6':
            symbol = input("Symbol (leave blank for all): ").strip()
            args = Namespace(symbol=symbol if symbol else None)
            handle_positions(args)
            
        elif choice == '7':
            handle_health(Namespace())
            
        elif choice == '8':
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
    
    # Account command
    subparsers.add_parser("account", help="Check account balances")
    
    # Open Orders command
    open_orders_parser = subparsers.add_parser("open-orders", help="Check open orders")
    open_orders_parser.add_argument("--symbol", required=False, default=None, help="Optional trading symbol")
    
    # Positions command
    positions_parser = subparsers.add_parser("positions", help="Check active positions")
    positions_parser.add_argument("--symbol", required=False, default=None, help="Optional trading symbol")
    
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
    elif args.command == "account":
        handle_account(args)
    elif args.command == "open-orders":
        handle_open_orders(args)
    elif args.command == "positions":
        handle_positions(args)
    elif args.command == "health":
        handle_health(args)
    elif args.command == "interactive":
        interactive_menu()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
