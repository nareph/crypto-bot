from discord.ext import commands
import discord
from src.utils.constants import SUPPORTED_SYMBOLS

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def show_help(self, ctx):
        embed = discord.Embed(
            title="💎 Crypto Bot Help",
            description="All commands use Binance API data",
            color=0xF0B90B
        )
        
        embed.add_field(
            name="💰 !price [symbol]",
            value=f"Get current price\nSupported: {', '.join(SUPPORTED_SYMBOLS.keys())}\nEx: `!price eth`",
            inline=False
        )
        
        embed.add_field(
            name="📊 !chart [symbol] [days]",
            value="Generate price chart (1-90 days)\nEx: `!chart btc 30`",
            inline=False
        )
        
        embed.add_field(
            name="🔔 !alert [symbol] [condition]",
            value="Set price alert (DMs when triggered)\nEx: `!alert sol >50`",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))