import subprocess
from PIL import Image, ImageDraw, ImageFont
import os

commands = {
    "health.png": "python cli.py health",
    "market_order.png": "python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001",
    "limit_order.png": "python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 150000",
    "stop_limit_order.png": "python cli.py place --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 95000 --stop-price 94000",
    "account.png": "python cli.py account",
    "positions.png": "python cli.py positions"
}

os.makedirs("screenshots", exist_ok=True)

try:
    font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 16)
except Exception:
    font = ImageFont.load_default()

def render_terminal(cmd, filename):
    print(f"Running {cmd}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    text = f"$ {cmd}\n{result.stdout}{result.stderr}"
    
    lines = text.split('\n')
    
    max_w = 0
    for line in lines:
        if hasattr(font, "getlength"):
            w = int(font.getlength(line))
        else:
            w = len(line) * 10
        if w > max_w:
            max_w = w
            
    width = max(800, max_w + 40)
    height = max(400, len(lines) * 22 + 40)
    
    img = Image.new('RGB', (width, height), color='#1e1e1e')
    d = ImageDraw.Draw(img)
    
    y = 20
    for line in lines:
        d.text((20, y), line, fill='#d4d4d4', font=font)
        y += 22
        
    img.save(f"screenshots/{filename}")
    print(f"Saved screenshots/{filename}")

for filename, cmd in commands.items():
    render_terminal(cmd, filename)
