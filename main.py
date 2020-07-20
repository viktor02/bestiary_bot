import configparser
import logging

import pymysql
import pymysql.cursors

from contextlib import closing
from aiogram import Bot, Dispatcher, executor, types

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read config
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize bot and dispatcher
bot = Bot(token=config['telegram']['TOKEN'])
dp = Dispatcher(bot)


@dp.message_handler(commands='help')
async def help_cmd(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    help_answer = "Привет! \n" \
            "Этот бот позволяет тебе быстро узнать, что за существо попалось тебе в̶ ̶р̶у̶к̶и̶ в книжке. \n" \
            "Просто введи название существа и я скажу, если знаю его. \n\n" \
            "Команды: " \
            "/help - помощь \n" \
            "/dev <i>текст_сообщения</i> - написать разработчику \n" \
            "<i>текст_поиска</i> - поиск по существу \n\n" \
            "Разработчик: vitka-k.ru \n" \
            "База данных: портал www.bestiary.us"

    await message.answer(help_answer)


@dp.message_handler(regexp='^\/')
async def not_found_cmd(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer("Команда не найдена! Справка: /help")


@dp.message_handler()
async def bestiary(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    con = pymysql.connect(host=config['mysql']['HOST'],
                          user=config['mysql']['USER'],
                          password=config['mysql']['PASS'],
                          db=config['mysql']['DB'],
                          charset=config['mysql']['CHARSET'],
                          cursorclass=pymysql.cursors.DictCursor)

    with closing(con) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM admin_terms.terms WHERE term LIKE %s ORDER BY term ASC LIMIT 2;",
                           ('%' + message.text + '%',))
            row = cursor.fetchall()



    text = "<i>Существо #%s </i>\n" \
           "<i>Название:</i> %s\n\n" \
           "Описание: %s \n\n" \
           "<a href='%s'>Подробнее</a> \n\n " \
           "Но, быть может, вы искали термин <i>%s?</i> " % (row[0]['id'],
                                                           row[0]['term'],
                                                           row[0]['value'],
                                                           row[0]['url'],
                                                           row[1]['term']
                                                           )

    await message.answer(text, 'html')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
