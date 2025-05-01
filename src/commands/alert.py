from discord.ext import commands
from src.utils.constants import SUPPORTED_SYMBOLS

class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="alert")
    async def set_alert(self, ctx, symbol: str, condition: str):
        """Set price alert (e.g. !alert btc >50000)"""
        if symbol.upper() not in SUPPORTED_SYMBOLS:
            await ctx.send(f"❌ Unsupported symbol. Use: {', '.join(SUPPORTED_SYMBOLS.keys())}")
            return

        try:
            # Validation de la condition
            test_value = 100
            if not eval(f"{test_value} {condition}"):
                raise ValueError("Invalid condition syntax")

            self.bot.user_alerts[ctx.author.id] = {
                'symbol': SUPPORTED_SYMBOLS[symbol.upper()],
                'condition': condition,
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
                f"`!alert eth <2000` - If ETH < $2K"
            )

async def setup(bot):
    await bot.add_cog(Alert(bot))