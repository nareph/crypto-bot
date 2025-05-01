import pytest
from src.bot import bot  # Importez les fonctions testables

def test_bot_initialization():
    """Vérifie que le bot peut s'initialiser"""
    assert bot.command_prefix == "!", "Le préfixe de commande est incorrect"
    
# Exemple de test avec mocking (à compléter)
@pytest.mark.asyncio
async def test_price_command():
    """Test simulé de la commande !price"""
    # Vous utiliserez des mocks pour simuler Discord et l'API Binance
    pass