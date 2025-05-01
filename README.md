# 💰 Crypto Price Bot

![Python](https://img.shields.io/badge/python-3.9+-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-green)
![Binance API](https://img.shields.io/badge/Binance-API-yellow)

A Discord bot that fetches real-time cryptocurrency prices and charts from Binance API, with price alert functionality.

## ✨ Features

| Command | Description | Example |
|---------|-------------|---------|
| `!help` | Shows all available commands | `!help` |
| `!price [symbol]` | Get current price with 24h change | `!price eth` |
| `!chart [symbol] [days]` | Generate price chart (1-90 days) | `!chart btc 30` |
| `!alert [symbol] [condition]` | Set price alert (DM when triggered) | `!alert sol >50` |

## 🚀 Setup

### Prerequisites
- Python 3.9+
- Discord Bot Token
- Binance API access (public endpoints used)

### Installation
```bash
# Clone the repository
git clone https://github.com/nareph/crypto-bot.git
cd crypto-bot

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env