#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import configparser

import pymysql
import pymysql.cursors

from contextlib import closing
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Read config
config = configparser.ConfigParser()
config.read('config.ini')

# Set logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start_command(update, context):
    update.message.reply_text('Hi!')


def help_command(update, context):
    update.message.reply_text('Help!')


def bestiary(update, context):
    con = pymysql.connect(host=config['mysql']['HOST'],
                          user=config['mysql']['USER'],
                          password=config['mysql']['PASS'],
                          db=config['mysql']['DB'],
                          charset=config['mysql']['CHARSET'],
                          cursorclass=pymysql.cursors.DictCursor)

    with closing(con) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM admin_terms.terms WHERE term LIKE %s ORDER BY term ASC LIMIT 2;",
                           ('%' + update.message.text + '%',))
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
    update.message.reply_text(text, 'html')


def main():
    updater = Updater(config['telegram']['TOKEN'], use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, bestiary))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
