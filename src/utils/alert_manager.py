import requests
from src.utils.constants import BINANCE_API

async def check_alerts(bot):
    for user_id, alert in list(bot.user_alerts.items()):
        try:
            # Récupère le prix actuel
            price_url = f"{BINANCE_API}/ticker/price?symbol={alert['symbol']}"
            price_data = requests.get(price_url).json()
            current_price = float(price_data['price'])

            # Vérifie la condition
            if eval(f"{current_price} {alert['condition']}"):
                user = await bot.fetch_user(user_id)
                await user.send(
                    f"🚨 **ALERT TRIGGERED**\n"
                    f"{alert['display_symbol']} {alert['condition']}\n"
                    f"Current price: **${current_price:,.2f}**\n"
                    f"_(Source: Binance)_"
                )
                del bot.user_alerts[user_id]

        except Exception as e:
            print(f"Alert check failed: {e}")