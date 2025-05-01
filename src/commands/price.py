from discord.ext import commands
from src.utils.binance import get_binance_data
from src.utils.constants import SUPPORTED_SYMBOLS

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="price")
    async def crypto_price(self, ctx, symbol: str):
        """Get crypto price (e.g. !price btc)"""
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

async def setup(bot):
    await bot.add_cog(Price(bot))