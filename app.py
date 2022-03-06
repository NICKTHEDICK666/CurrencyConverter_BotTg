import telebot
import requests
import json
from config import keys, TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands= ['start'])
def welcome_message(message):
    bot.send_message(message.chat.id, f'Привет, {message.chat.username}. \nЧтобы узнать, как пользоваться '
                                      f'ботом, введи команду /help')

@bot.message_handler(commands= ['help'])
def values_message(message):
    bot.send_message(message.chat.id, f'Чтобы воспользоваться ботом отправь сообщение вида: \n'
                                      f'<имя валюты, цену которой хочешь узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты> \n'
                                      f'Увидеть список всех доступных валют, введи команду /values')

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = "\n".join((text, key))
    bot.send_message(message.chat.id, text)


class ConvertionExeption(Exception):
    pass


@bot.message_handler(content_types=['text', ])
def converter(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise ConvertionExeption('Слишком много параметров.')

        quote, base, amount = values

        if quote == base:
            raise ConvertionExeption(f'Невозможно перевести одинаковые валюты {base}')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionExeption(f'Не удалось обработать количество {amount}')

        r = requests.get(f'https://free.currconv.com/api/v7/convert?q={quote_ticker}_{base_ticker}&compact=ultra&apiKey=d84cf1bb0ece1d1a78a5')
        total_base = json.loads(r.content)
        total_base = list(total_base.values())
    except ConvertionExeption as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду.\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {float(*total_base) * amount}'
        bot.send_message(message.chat.id, text)





bot.polling(none_stop=True)