import sys
sys.path.insert(0, '../')

import telebot
import config

from db_utils.database_manage import UsersLists

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=["start"])
def handle_start_message(message):
    bot.send_message(message.chat.id, config.BOT_GREETING, parse_mode="markdown")

bot.polling()