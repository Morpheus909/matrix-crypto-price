📦 Requirements:
Python

pip install aiogram
pip install requests

🔑 Bot Token
Go to @BotFather

Create a bot using /newbot

Copy the token

Replace the placeholder in the script:
API_TOKEN = 'PASTE_YOUR_BOT_TOKEN_HERE'

▶️ Run the Bot
python bot.py

🔁 Supported Commands
Command	Description
/start	Start the bot & choose language
/language	Change language manually
/help	Show usage instructions

💡 Customization
To add more cryptocurrencies:

CRYPTO_MAPPING = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    ...
}
To update exchange rates (manual fallback):

def get_exchange_rate(currency: str):
    rates = {
        'usd': 1,
        'eur': 0.93,
        'pln': 4.30,
    }

🛡️ Disclaimer
Prices are fetched from CoinGecko and are for informational purposes only. This is not financial advice.

🧑‍💻 Author
Created by Morpheus909
Inspired by The Matrix. 🕶️
