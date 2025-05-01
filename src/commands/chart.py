from discord.ext import commands
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from src.utils.constants import SUPPORTED_SYMBOLS, BINANCE_API

class Chart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chart")
    async def price_chart(self, ctx, symbol: str, days: int = 7):
        """Generate price chart (e.g. !chart eth 30)"""
        if symbol.upper() not in SUPPORTED_SYMBOLS:
            await ctx.send(f"❌ Unsupported symbol. Use: {', '.join(SUPPORTED_SYMBOLS.keys())}")
            return

        try:
            binance_symbol = SUPPORTED_SYMBOLS[symbol.upper()]
            interval = '1d' if days > 1 else '1h'
            limit = min(days, 90) if days > 1 else 24
            
            url = f"{BINANCE_API}/klines?symbol={binance_symbol}&interval={interval}&limit={limit}"
            data = requests.get(url).json()
            
            dates = [entry[0] for entry in data]
            prices = [float(entry[4]) for entry in data]

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

async def setup(bot):
    await bot.add_cog(Chart(bot))