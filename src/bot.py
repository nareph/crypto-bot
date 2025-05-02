import discord
from discord.ext import commands, tasks 
from dotenv import load_dotenv
import os
import sys
import logging
from pathlib import Path
import traceback

# Advanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger('CryptoBot')
discord.utils.setup_logging(handler=logging.FileHandler('discord.log'))

# Path configuration
sys.path.append(str(Path(__file__).parent))

load_dotenv()

class CryptoBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            help_command=None,
            chunk_guilds_at_startup=False,  # Memory optimization
            member_cache_flush_time=300     # Cache reduction
        )
        self.user_alerts = {}
        self.start_time = None

    async def setup_hook(self):
        """Bot initialization setup"""
        self.start_time = discord.utils.utcnow()
        logger.info("Starting setup_hook")
        
        # Extension loading with error handling
        extensions = [
            'src.commands.price',
            'src.commands.chart', 
            'src.commands.alert',
            'src.commands.help'
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Successfully loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load {ext}: {traceback.format_exc()}")
                continue

        # Background task verification
        if not self.check_alerts.is_running():
            self.check_alerts.start()
            logger.info("Started check_alerts background task")

    @tasks.loop(minutes=5)
    async def check_alerts(self):
        """Periodic alert checking"""
        try:
            from src.utils.alert_manager import check_alerts
            logger.debug("Starting alert checks")
            await check_alerts(self)
        except Exception as e:
            logger.error(f"Alert check error: {traceback.format_exc()}")

    @check_alerts.before_loop
    async def before_check_alerts(self):
        """Wait until bot is ready"""
        await self.wait_until_ready()
        logger.info("Bot ready for alert checks")

    async def on_ready(self):
        """Connection handler"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Current latency: {round(self.latency * 1000)}ms")
        logger.info(f"Connected to {len(self.guilds)} servers")

    async def on_error(self, event, *args, **kwargs):
        """Global error handler"""
        logger.error(f"Error in {event}: {traceback.format_exc()}")

bot = CryptoBot()

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        bot.run(os.getenv("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        logger.info("Manual bot shutdown")
    except Exception as e:
        logger.critical(f"Fatal error: {traceback.format_exc()}")
    finally:
        logger.info("Bot shutdown complete")
