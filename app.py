import telebot
from telebot.types import Message
import requests
import os

# Загрузка токена из переменной окружения
TOKEN = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Ваш API key для Yandex Geocoder
YANDEX_GEOCODER_API_KEY = os.getenv('YANDEX_GEOCODER_API_KEY')

BASE_URL = "https://geocode-maps.yandex.ru/1.x/"

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(
        message.chat.id,
        "Привет! В этом боте ты можешь легко конвертировать почтовый индекс в адрес!\nПросто отправь боту индекс и мгновенно получи адрес."
    )

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message: Message):
    index = message.text.strip()
    if len(index) != 6 or not index.isdigit():  # Проверка формата индекса
        return bot.send_message(message.chat.id, "Неправильный формат индекса. Отправьте шестизначный номер.")

    # Показ статуса ожидания
    msg_id = bot.send_message(message.chat.id, "Ищу адрес...").message_id

    try:
        params = {
            "format": "json",
            "apikey": YANDEX_GEOCODER_API_KEY,
            "geocode": index
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'response' in data and data['response']['GeoObjectCollection']['featureMember']:
            geo_object = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            postal_code = geo_object['metaDataProperty']['GeocoderMetaData'].get('AddressDetails', {}).get('Country', {}).get('AdministrativeArea', {}).get('Locality', {})
            result_address = geo_object['description'] + ', ' + geo_object['name']
            
            # Удаляем сообщение "Ищу адрес..."
            bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            
            # Возвращаем полученный адрес
            bot.send_message(message.chat.id, f"Ваш адрес: {result_address}")
            
            # Благодарность пользователю
            bot.send_message(message.chat.id, "Спасибо за использование нашего бота!")
        else:
            raise ValueError("Адрес не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
Что изменилось:
Вместо GeoDB используется Yandex Geocoder API.
Изменены параметры запроса к серверу (формат JSON, geocode и apikey).
Извлекаются нужные поля из ответа сервера Yandex.
Ограничения и особенности Yandex Geocoder API:
Бесплатный режим Yandex API позволяет совершать до 25 тысяч запросов в сутки.
Для коммерческих проектов может потребоваться платная версия.
Важные моменты:
Обязательно храните ключи API в скрытых переменных окружения, чтобы избежать утечек конфиденциальных данных.
Обратите внимание на политику использования API Yandex и соблюдайте правила использования.
Теперь ваш бот полноценно функционирует на территории России благодаря поддержке отечественного сервиса Yandex Maps API.
