import telebot
from telebot.types import Message
import requests
import os

# Загрузка токена из переменной окружения
TOKEN = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(
        message.chat.id,
        "Привет! В этом боте ты можешь легко конвертировать почтовый индекс в адрес!\\nПросто отправь боту индекс и мгновенно получи адрес."
    )

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message: Message):
    index = message.text.strip()
    if len(index) != 6 or not index.isdigit():  # Проверка формата индекса
        return bot.send_message(message.chat.id, "Неправильный формат индекса. Отправьте шестизначный номер.")

    # Показ статуса ожидания
    msg_id = bot.send_message(message.chat.id, "Ищу адрес...").message_id

    try:
        # Формируем запрос к поисковой строке Яндекс
        search_url = f"https://yandex.ru/search/?text=почтовый индекс {index}"
        response = requests.get(search_url)
        response.raise_for_status()

        # Здесь можно добавить логику для парсинга результатов поиска
        # Например, можно использовать BeautifulSoup для извлечения данных из HTML

        # Примерный результат (для демонстрации)
        address = "Примерный адрес, который был найден в поиске"

        # Удаляем сообщение "Ищу адрес..."
        bot.delete_message(chat_id=message.chat.id, message_id=msg_id)

        # Возвращаем полученный адрес
        bot.send_message(message.chat.id, f"Ваш адрес: {address}")

        # Благодарность пользователю
        bot.send_message(message.chat.id, "Спасибо за использование нашего бота!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
