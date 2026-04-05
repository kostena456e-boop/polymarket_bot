
import os
import telebot
from telebot import types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 Анализировать событие"))
    markup.add(types.KeyboardButton("❓ Как пользоваться"))
    bot.send_message(message.chat.id,
        "👋 Привет! Я помогаю анализировать события на Polymarket.\n\n"
        "Зайди на polymarket.com, найди интересное событие и напиши мне:\n"
        "• Название события\n"
        "• Текущую вероятность %\n"
        "• Объём торгов $\n\n"
        "Я скажу стоит ли ставить!",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "❓ Как пользоваться")
def help(message):
    bot.send_message(message.chat.id,
        "📖 *Как пользоваться:*\n\n"
        "1️⃣ Зайди на polymarket.com\n"
        "2️⃣ Найди событие которое тебя интересует\n"
        "3️⃣ Напиши мне в формате:\n\n"
        "*Событие: Выиграет ли Трамп*\n"
        "*Вероятность: 45%*\n"
        "*Объём: 50000*\n\n"
        "4️⃣ Я проанализирую и дам совет!",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 Анализировать событие")
def analyze_prompt(message):
    bot.send_message(message.chat.id,
        "Напиши мне информацию о событии в таком формате:\n\n"
        "Событие: [название]\n"
        "Вероятность: [число]%\n"
        "Объём: [число]")

@bot.message_handler(func=lambda m: "событие:" in m.text.lower())
def analyze(message):
    try:
        lines = message.text.strip().split("\n")
        question = ""
        prob = 0
        volume = 0
        for line in lines:
            if "событие:" in line.lower():
                question = line.split(":", 1)[1].strip()
            elif "вероятность:" in line.lower():
                prob = int(''.join(filter(str.isdigit, line)))
            elif "объём:" in line.lower() or "объем:" in line.lower():
                volume = int(''.join(filter(str.isdigit, line)))

        if prob < 20:
            вывод = "🔴 Очень маловероятно. Высокий риск."
            совет = "Ставь ДА только если очень уверен — потенциал высокий но риск большой"
        elif prob < 40:
            вывод = "🟡 Рынок считает маловероятным"
            совет = "Если у тебя есть информация что вероятность выше — хорошая возможность поставить ДА"
        elif prob < 60:
            вывод = "⚪️ Неопределённость — рынок не знает"
            совет = "Жди новостей по этой теме — они сдвинут цену"
        elif prob < 80:
            вывод = "🟡 Рынок считает вероятным"
            совет = "Если сомневаешься — поставь НЕТ, потенциал есть"
        else:
            вывод = "🟢 Рынок считает почти точным"
            совет = "Ставить ДА невыгодно — маленькая прибыль. Ставь НЕТ если есть сомнения"

        if volume > 100000:
            ликвидность = "✅ Высокий объём — хорошая ликвидность"
        elif volume > 10000:
            ликвидность = "⚠️ Средний объём — нормально"
        else:
            ликвидность = "❌ Низкий объём — осторожно"

        msg = (
            f"📊 *Анализ события:*\n"
            f"_{question}_\n\n"
            f"💰 Вероятность: *{prob}%*\n"
            f"{вывод}\n\n"
            f"{ликвидность}\n\n"
            f"💡 *Совет:*\n{совет}\n\n"
            f"⚠️ Не ставь больше 10$ пока не набьёшь руку!"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id,
            "Не смог разобрать. Напиши в формате:\n\n"
            "Событие: название\n"
            "Вероятность: 45%\n"
            "Объём: 50000")

bot.polling(none_stop=True)
