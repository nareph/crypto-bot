import requests
from src.utils.constants import BINANCE_API, SUPPORTED_SYMBOLS

def get_binance_data(symbol: str):
    """Récupère les données de Binance avec vérification"""
    try:
        symbol = symbol.upper()
        if symbol not in SUPPORTED_SYMBOLS:
            return None, "Unsupported symbol"

        binance_symbol = SUPPORTED_SYMBOLS[symbol]
        
        # Requête pour le prix actuel
        price_url = f"{BINANCE_API}/ticker/price?symbol={binance_symbol}"
        price_data = requests.get(price_url).json()
        
        # Requête pour les changements 24h
        ticker_url = f"{BINANCE_API}/ticker/24hr?symbol={binance_symbol}"
        ticker_data = requests.get(ticker_url).json()
        
        return {
            'price': float(price_data['price']),
            'change': float(ticker_data['priceChangePercent'])
        }, None
    except Exception as e:
        return None, str(e)