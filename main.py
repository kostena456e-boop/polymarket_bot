
import os
import requests
import telebot
from telebot import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_polymarket_events():
    url = "https://gamma-api.polymarket.com/markets?closed=false&limit=50&sort=volume&order=DESC"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except:
        return []

def analyze_events(events):
    opportunities = []
    for event in events:
        try:
            question = event.get("question", "")
            if not question:
                continue
            volume = float(event.get("volume", 0) or 0)
            if volume < 100:
                continue
            prices_raw = event.get("outcomePrices", "")
            if not prices_raw:
                continue
            prices_raw = prices_raw.strip("[]").split(",")
            price = float(prices_raw[0].strip().strip('"'))
            price_pct = round(price * 100)
            opportunities.append({
                "question": question,
                "price": price_pct,
                "volume": round(volume)
            })
        except:
            continue
    return opportunities[:5]

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔍 Найти возможности"))
    bot.send_message(message.chat.id,
        "👋 Привет! Я показываю топ события на Polymarket.\n\nНажми кнопку чтобы начать!",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔍 Найти возможности")
def scan(message):
    bot.send_message(message.chat.id, "⏳ Загружаю события с Polymarket...")
    events = get_polymarket_events()
    if not events:
        bot.send_message(message.chat.id, "❌ Не удалось получить данные.")
        return
    opportunities = analyze_events(events)
    if not opportunities:
        bot.send_message(message.chat.id, "😔 Нет событий. Попробуй позже.")
        return
    for op in opportunities:
        if op['price'] < 50:
            совет = "💡 Рынок считает маловероятным — ставь ДА если не согласен"
        else:
            совет = "💡 Рынок считает вероятным — ставь НЕТ если сомневаешься"
        msg = (
            f"🎯 *{op['question']}*\n\n"
            f"📊 Вероятность: *{op['price']}%*\n"
            f"💰 Объём: ${op['volume']}\n"
            f"{совет}\n\n"
            f"🔗 polymarket.com"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

bot.polling(none_stop=True)
