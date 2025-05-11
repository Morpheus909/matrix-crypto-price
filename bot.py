import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = 'token' 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher()

LANGUAGES = {
    'en': {
        'start': '🌐 Welcome to the Matrix! Your gateway to real-time crypto prices. Choose your currency pair! 💸',
        'currency_choice': '💰 Choose the currency you want to view prices in:',
        'crypto_choice': '⚡ Choose a cryptocurrency to track:',
        'price': '📉 Current price of {crypto}: {price} {currency} 🔥',
        'error': '❌ Something went wrong! Please try again. 🚨',
        'language_choice': '🌍 Choose your language to dive in:'
    },
    'pl': {
        'start': '🌐 Witaj w Matrixie! Twoje przejście do aktualnych cen kryptowalut w czasie rzeczywistym. Wybierz parę walutową! 💸',
        'currency_choice': '💰 Wybierz walutę, w której chcesz zobaczyć ceny:',
        'crypto_choice': '⚡ Wybierz kryptowalutę do śledzenia:',
        'price': '📉 Aktualna cena {crypto}: {price} {currency} 🔥',
        'error': '❌ Coś poszło nie tak! Spróbuj ponownie. 🚨',
        'language_choice': '🌍 Wybierz język, aby zanurzyć się w Matrixie:'
    },
    'ru': {
        'start': '🌐 Добро пожаловать в Matrix! Ваш путь к актуальным ценам криптовалют в реальном времени. Выберите валютную пару! 💸',
        'currency_choice': '💰 Выберите валюту, в которой хотите увидеть цены:',
        'crypto_choice': '⚡ Выберите криптовалюту для отслеживания:',
        'price': '📉 Текущая цена {crypto}: {price} {currency} 🔥',
        'error': '❌ Что-то пошло не так! Попробуйте снова. 🚨',
        'language_choice': '🌍 Выберите язык, чтобы погрузиться в Matrix:'
    }
}

user_data = {}

CRYPTO_MAPPING = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'xmr': 'monero',
    'ltc': 'litecoin',
    'sol': 'solana',
    'xrp': 'ripple'
}

def get_crypto_price(crypto: str, currency: str):
    """Get cryptocurrency price in selected currency."""
    crypto_full_name = CRYPTO_MAPPING.get(crypto, crypto)  

    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_full_name}&vs_currencies=usd'
    response = requests.get(url).json()

    print(f"API Response for {crypto_full_name} in USD: {response}")

    if response and crypto_full_name in response and 'usd' in response[crypto_full_name]:
        price_in_usd = response[crypto_full_name]['usd']
        exchange_rate = get_exchange_rate(currency)
        if exchange_rate:
            return price_in_usd * exchange_rate
        return None
    return None

def get_exchange_rate(currency: str):
    """Get the exchange rate from USD to the selected currency."""
    rates = {
        'usd': 1,  
        'eur': 0.93,  
        'pln': 4.30,  
    }
    return rates.get(currency)

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_data[message.chat.id] = {'language': 'en', 'currency': 'usd'}  
    await message.reply(LANGUAGES['en']['start'], reply_markup=language_keyboard())

def language_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='English 🌍', callback_data='lang_en')],
            [InlineKeyboardButton(text='Polski 🇵🇱', callback_data='lang_pl')],
            [InlineKeyboardButton(text='Русский 🇷🇺', callback_data='lang_ru')]
        ]
    )
    return keyboard

@dp.message(Command('language'))
async def cmd_change_language(message: types.Message):
    user_data[message.chat.id]['language'] = 'en'  
    await message.reply(LANGUAGES[user_data[message.chat.id]['language']]['language_choice'], reply_markup=language_keyboard())

@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def choose_language(callback: types.CallbackQuery):
    lang_choice = callback.data.split('_')[1]
    user_data[callback.from_user.id]['language'] = lang_choice
    await callback.message.answer(LANGUAGES[lang_choice]['start'], reply_markup=currency_keyboard())
    await callback.answer()

def currency_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='USD 💵', callback_data='currency_usd')],
            [InlineKeyboardButton(text='EUR 💶', callback_data='currency_eur')],
            [InlineKeyboardButton(text='PLN 🇵🇱', callback_data='currency_pln')]
        ]
    )
    return keyboard

@dp.callback_query(lambda c: c.data.startswith('currency_'))
async def select_currency(callback: types.CallbackQuery):
    currency = callback.data.split('_')[1]
    user_data[callback.from_user.id]['currency'] = currency
    await callback.message.answer(LANGUAGES[user_data[callback.from_user.id]['language']]['crypto_choice'], reply_markup=crypto_keyboard())
    await callback.answer()

def crypto_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='BTC 🪙', callback_data='crypto_btc')],
            [InlineKeyboardButton(text='ETH ⚙️', callback_data='crypto_eth')],
            [InlineKeyboardButton(text='XMR 🕶️', callback_data='crypto_xmr')],
            [InlineKeyboardButton(text='LTC 🔥', callback_data='crypto_ltc')],
            [InlineKeyboardButton(text='SOL ☀️', callback_data='crypto_sol')],
            [InlineKeyboardButton(text='XRP 🌊', callback_data='crypto_xrp')]
        ]
    )
    return keyboard

@dp.callback_query(lambda c: c.data.startswith('crypto_'))
async def show_price(callback: types.CallbackQuery):
    crypto_choice = callback.data.split('_')[1]
    currency = user_data.get(callback.from_user.id, {}).get('currency', 'usd')
    price = get_crypto_price(crypto_choice, currency)

    if price:
        price_str = f"{price:.2f}"  
        await callback.message.answer(
            LANGUAGES[user_data[callback.from_user.id]['language']]['price'].format(
                crypto=crypto_choice.upper(), price=price_str, currency=currency
            )
        )
    else:
        await callback.message.answer(LANGUAGES[user_data[callback.from_user.id]['language']]['error'])
    await callback.answer()

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.reply(
        '💡 *How to use this bot?* 🤖\n\n'
        '1️⃣ Choose your preferred language (English, Polish, Russian).\n'
        '2️⃣ Select your fiat currency (USD, EUR, PLN).\n'
        '3️⃣ Pick a cryptocurrency (BTC, ETH, SOL, XMR, etc.).\n'
        '4️⃣ The bot will show you the current price of your crypto in the selected currency. 💸\n\n'
        'Stay tuned for more features! 🚀\n\n'
        'Made by: **https://github.com/Morpheus909** 🕶️'
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
