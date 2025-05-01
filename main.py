import os
import discord
from discord.ext import commands, tasks
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from dotenv import load_dotenv
import time

# Configuration
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BINANCE_API = "https://api.binance.us/api/v3"

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
user_alerts = {}

# Liste complète des symboles supportés
SUPPORTED_SYMBOLS = {
    'BTC': 'BTCUSDT',
    'ETH': 'ETHUSDT',
    'BNB': 'BNBUSDT',
    'SOL': 'SOLUSDT',
    'XRP': 'XRPUSDT',
    'ADA': 'ADAUSDT',
    'DOGE': 'DOGEUSDT',
    'DOT': 'DOTUSDT',
    'SHIB': 'SHIBUSDT',
    'AVAX': 'AVAXUSDT'
}

def get_binance_data(symbol: str):
    """Récupère les données de Binance avec vérification"""
    try:
        symbol = symbol.upper()
        # Vérifie d'abord si le symbole est supporté
        if symbol not in SUPPORTED_SYMBOLS:
            return None, "Unsupported symbol"

        binance_symbol = SUPPORTED_SYMBOLS[symbol]
        print(f"Requesting price for symbol: {binance_symbol}")

        # Requête pour le prix actuel
        price_url = f"{BINANCE_API}/ticker/price?symbol={binance_symbol}"
        price_response = requests.get(price_url)
        if not price_response.ok:
            return None, f"Binance API error: {price_response.status_code} - {price_response.text}"
            
        price_data = price_response.json()
        if 'price' not in price_data:
            return None, f"Invalid price data from Binance: {price_data}"

        # Requête pour les changements 24h
        ticker_url = f"{BINANCE_API}/ticker/24hr?symbol={binance_symbol}"
        ticker_response = requests.get(ticker_url)
        ticker_data = ticker_response.json()
        
        if 'priceChangePercent' not in ticker_data:
            return None, "Failed to get ticker data from Binance"

        return {
            'price': float(price_data['price']),
            'change': float(ticker_data['priceChangePercent'])
        }, None

    except requests.exceptions.RequestException:
        return None, "Failed to connect to Binance API"
    except (ValueError, KeyError) as e:
        return None, f"Invalid data received from Binance: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# -----------------------------------------------------------
# Commandes corrigées
# -----------------------------------------------------------

@bot.command(name="price")
async def crypto_price(ctx, symbol: str):
    """Affiche le prix d'une crypto (ex: !price btc)"""
    data, error = get_binance_data(symbol)

    if error:
        await ctx.send(
            f"❌ Error: {error}\n"
            f"Supported symbols: {', '.join(SUPPORTED_SYMBOLS.keys())}"
        )
        return

    await ctx.send(
        f"**{symbol.upper()}**\n"
        f"Price: **${data['price']:,.2f}**\n"
        f"24h change: {data['change']:+.2f}%\n"
        f"_(Source: Binance)_"
    )

@bot.command(name="chart")
async def price_chart(ctx, symbol: str, days: int = 7):
    """Génère un graphique de prix (ex: !chart eth 30)"""
    if symbol.upper() not in SUPPORTED_SYMBOLS:
        await ctx.send(f"❌ Unsupported symbol. Use: {', '.join(SUPPORTED_SYMBOLS.keys())}")
        return

    try:
        binance_symbol = SUPPORTED_SYMBOLS[symbol.upper()]
        interval = '1d' if days > 1 else '1h'
        limit = min(days, 90) if days > 1 else 24  # Limite à 90 jours max

        url = f"{BINANCE_API}/klines?symbol={binance_symbol}&interval={interval}&limit={limit}"
        response = requests.get(url)
        data = response.json()

        if not data or len(data) == 0:
            raise ValueError("No data returned from Binance")

        dates = [entry[0] for entry in data]
        prices = [float(entry[4]) for entry in data]  # Prix de clôture

        plt.style.use('dark_background')
        plt.figure(figsize=(10, 5))
        plt.plot(dates, prices, color='#F0B90B', linewidth=2)
        plt.title(f"{symbol.upper()} Price ({days} days)")
        plt.ylabel("Price (USDT)")
        plt.xticks(rotation=45)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        await ctx.send(
            file=discord.File(buf, f"{symbol}_chart.png"),
            content=f"📊 **{symbol.upper()}** Price Chart | {days} days (Source: Binance)"
        )
        plt.close()

    except Exception as e:
        await ctx.send(f"❌ Chart error: {str(e)}")

@bot.command(name="alert")
async def set_alert(ctx, symbol: str, condition: str):
    """Configure une alerte (ex: !alert btc >50000)"""
    if symbol.upper() not in SUPPORTED_SYMBOLS:
        await ctx.send(f"❌ Unsupported symbol. Use: {', '.join(SUPPORTED_SYMBOLS.keys())}")
        return

    try:
        # Validate condition format
        if not any(op in condition for op in ['>', '<', '>=', '<=']):
            raise ValueError("Invalid operator")
            
        # Extract numerical value
        value = float(''.join(c for c in condition if c.isdigit() or c == '.'))
        operator = ''.join(c for c in condition if c in '<>=')
        
        user_alerts[ctx.author.id] = {
            'symbol': SUPPORTED_SYMBOLS[symbol.upper()],
            'condition': f"{operator}{value}",
            'display_symbol': symbol.upper()
        }

        await ctx.send(
            f"✅ Alert set for **{symbol.upper()} {condition}**\n"
            f"You'll receive a DM when triggered."
        )

    except Exception as e:
        await ctx.send(
            f"❌ Invalid alert format. Examples:\n"
            f"`!alert btc >50000` - If BTC > $50K\n"
            f"`!alert eth <2000` - If ETH < $2K\n"
            f"Supported symbols: {', '.join(SUPPORTED_SYMBOLS.keys())}"
        )

@tasks.loop(minutes=5)
async def check_alerts():
    for user_id, alert in list(user_alerts.items()):
        try:
            price_url = f"{BINANCE_API}/ticker/price?symbol={alert['symbol']}"
            price_data = requests.get(price_url).json()
            current_price = float(price_data['price'])

            if eval(f"{current_price} {alert['condition']}"):
                user = await bot.fetch_user(user_id)
                await user.send(
                    f"🚨 **ALERT**: {alert['display_symbol']} {alert['condition']}\n"
                    f"Current price: ${current_price:,.2f}\n"
                    f"(Source: Binance)"
                )
                del user_alerts[user_id]

        except Exception as e:
            print(f"Alert error: {e}")

# -----------------------------------------------------------
# Help Command amélioré
# -----------------------------------------------------------

@bot.command(name="help_command")
async def show_help(ctx):
    embed = discord.Embed(
        title="💎 Crypto Bot Help",
        description="All commands use Binance API data",
        color=0x00ff00
    )

    embed.add_field(
        name="💰 !price [symbol]",
        value=f"Get current price\nSupported: {', '.join(SUPPORTED_SYMBOLS.keys())}\nEx: `!price eth`",
        inline=False
    )

    embed.add_field(
        name="📈 !chart [symbol] [days]",
        value="Generate price chart (1-90 days)\nEx: `!chart btc 30`",
        inline=False
    )

    embed.add_field(
        name="🔔 !alert [symbol] [condition]",
        value="Set price alert (DMs when triggered)\nEx: `!alert sol >50`",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    check_alerts.start()

bot.run(TOKEN)