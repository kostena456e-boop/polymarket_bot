import os
import requests
import telebot
from telebot import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_polymarket_events():
    url = "https://gamma-api.polymarket.com/markets?closed=false&limit=20&sort=volume&order=DESC"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return []

def get_news(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3,
        "tbm": "nws"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        results = r.json().get("news_results", [])
        return results[:3]
    except:
        return []

def analyze_events(events):
    opportunities = []
    for event in events:
        try:
            question = event.get("question", "")
            price = float(event.get("outcomePrices", "[0.5]").strip("[]").split(",")[0])
            volume = float(event.get("volume", 0))
            if volume < 1000:
                continue
            news = get_news(question)
            if not news:
                continue
            if price < 0.3 or price > 0.7:
                opportunities.append({
                    "question": question,
                    "price": price,
                    "volume": volume,
                    "news": news[0]["title"] if news else "Нет новостей"
                })
        except:
            continue
    return opportunities[:3]

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("🔍 Найти возможности")
    markup.add(btn)
    bot.send_message(message.chat.id,
        "👋 Привет! Я помогаю находить выгодные события на Polymarket.\n\nНажми кнопку чтобы начать!",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔍 Найти возможности")
def scan(message):
    bot.send_message(message.chat.id, "⏳ Анализирую рынки Polymarket, подожди 10-20 секунд...")
    events = get_polymarket_events()
    if not events:
        bot.send_message(message.chat.id, "❌ Не удалось получить данные. Попробуй позже.")
        return
    opportunities = analyze_events(events)
    if not opportunities:
        bot.send_message(message.chat.id, "😔 Сейчас нет явных возможностей. Попробуй позже.")
        return
    for op in opportunities:
        price_pct = round(op['price'] * 100)
        direction = "📈 НИЗКАЯ цена" if op['price'] < 0.3 else "📉 ВЫСОКАЯ цена"
        msg = (
            f"🎯 *Возможность найдена!*\n\n"
            f"❓ *Событие:* {op['question']}\n\n"
            f"💰 *Текущая вероятность:* {price_pct}%\n"
            f"📊 *Объём торгов:* ${round(op['volume'])}\n"
            f"{direction}\n\n"
            f"📰 *Свежая новость:*\n{op['news']}\n\n"
            f"🔗 Проверь на polymarket.com"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

bot.polling(none_stop=True)
