import os
import telebot
import requests
from fastapi import FastAPI
import uvicorn

# Получаем токен бота из переменных окружения Render
TOKEN = os.getenv("TG_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Инициализируем FastAPI приложение
app = FastAPI()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Этот бот конвертирует почтовые индексы в адреса.\\nПросто пришли ему почтовый индекс и получи адрес."
    )

def get_address_by_postal_code(postal_code):
    """Получение адреса по почтовому индексу."""
    url = f"https://api.nalchikpost.ru/api/v1/address?postal_code={postal_code}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('address', 'Адрес не найден')
    else:
        return "Ошибка при запросе к API."

@bot.message_handler(func=lambda m: True)
def handle_postal_code(message):
    postal_code = message.text.strip()
    
    # Отправляем промежуточное сообщение о поиске адреса
    temp_msg = bot.send_message(message.chat.id, "Ищу адрес...")
    
    try:
        # Получаем адрес по почтовому индексу
        address = get_address_by_postal_code(postal_code)
        
        # Удаляем промежуточное сообщение
        bot.delete_message(temp_msg.chat.id, temp_msg.message_id)
        
        # Отправляем полученный адрес
        bot.send_message(message.chat.id, address)
        
        # Завершаем обработку сообщением благодарности
        bot.send_message(message.chat.id, "Спасибо за использование нашего бота!")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Что-то пошло не так при обработке вашего запроса :(")

# Запускаем бота
bot.infinity_polling()

# Настройка FastAPI для прослушивания порта
@app.get("/")
async def root():
    return {"message": "Telegram Postal Code to Address Bot is running!"}

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
