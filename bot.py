# -*- coding: utf-8 -*-

import config
import telebot
import signal
import time
import random

from storage import *
from pickle_api import *

bot = telebot.TeleBot(config.token)
state = config.States.default
form = {'type' : '',
        'object' : '',
        'description' : '',
        'message' : ''}

def signal_handler(signum, frame):
    print('\nGot SIGINT, stopping bot')
    save_obj(storage, 'storage')
    exit()


def trace_state():
    global state
    if state == config.States.waitObject:
        return 'Я жду отправки объекта для сохранения'
    elif state == config.States.waitDescrForAdd:
        return 'Я жду отправки описания объекта'


@bot.message_handler(commands=['add'])
def handle_add(message):
    global state
    if state == config.States.default:
        bot.send_message(message.chat.id, 'Отправьте текст(или картинку) для сохранения')
        state = config.States.waitObject
    else:
        bot.send_message(message.chat.id, trace_state())


@bot.message_handler(commands=['search'])
def handle_add(message):
    global state, storage
    if state == config.States.default:
        bot.send_message(message.chat.id, 'Введите описание объекта для поиска')
        state = config.States.waitDescrForSearch
    else:
        bot.send_message(message.chat.id, trace_state())


@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    global state
    if state == config.States.waitObject:
        bot.send_message(message.chat.id, 'Объект получен\nОтправьте описание')
        
        form['type'] = 'test'
        form['object'] = message.text
        form['message'] = message
        
        state = config.States.waitDescrForAdd
    elif state == config.States.waitDescrForAdd:
        bot.send_message(message.chat.id, 'Описание получено\nОбъект добавлен в хранилище')
        
        form['description'] = message.text
        print('Got form:', form)
        handle_form(storage, form)
    elif state == config.States.waitDescrForSearch:
        result = search(storage, message.text)
        if len(result) == 0:
            bot.send_message(message.chat.id, 'По запросу ничего не найдено :(\nПопробуйте другой запрос')
        else:
            bot.send_message(message.chat.id, 'Найдено ' + str(len(result)) + ' объектов')
            for msg in result:
                # print(msg)
                bot.reply_to(msg, '')
    else:
        print(message)
        bot.send_message(message.chat.id, 'Заглушка: ' + message.text)


@bot.message_handler(content_types=['photo'])
def photo(message):
    print('Got photo message\nBut I can\'t handle photo nowТы ')


@bot.message_handler(func=lambda m: True)
def others(message):
    print('Got unhandled messase')

if __name__ == '__main__':
    global storage

    signal.signal(signal.SIGINT, signal_handler)

    try:
        storage = load_obj('storage')
    except FileNotFoundError:
        storage = {}

    print('Bot is launched')
    
    # print(storage)
    # for term in storage:
    #     print(term, storage[term])

    bot.polling(none_stop=True)