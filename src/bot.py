import discord
from discord.ext import commands, tasks 
from dotenv import load_dotenv
import os

load_dotenv()

class CryptoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            help_command=None
        )
        self.user_alerts = {}

    async def setup_hook(self):
        # Chargement des commandes
        await self.load_extension('src.commands.price')
        await self.load_extension('src.commands.chart')
        await self.load_extension('src.commands.alert')
        await self.load_extension('src.commands.help')
        
        # Démarrage des tâches en arrière-plan
        self.check_alerts.start()

    @tasks.loop(minutes=5)
    async def check_alerts(self):
        from src.utils.alert_manager import check_alerts
        await check_alerts(self)

bot = CryptoBot()

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))