import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import config
import datetime

from telebot import TeleBot, types
from db_utils.database_manage import UserManager, UserListManager, DbTools
from keyboards_utils import set_main_menu_keyboard, set_time_format_keyboard
from functions_wrapps import next_step

bot = TeleBot(config.BOT_TOKEN)

remove_keyboard = types.ReplyKeyboardRemove(False)


# ! From the first view, it may be scary to read the code, but the majority of the code are just linked functions that are responsible for lists' creation


def choose_an_option(message):
    """A function that sets a further action"""
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    user_id = message.from_user.id

    if message.text == "🎲 Create":
        get_tuple =  DbTools.get_fields_from_table("users", "lists_count", f"id = {user_id}")
        lists_count = get_tuple[0] if get_tuple is not None else 0

        if lists_count >= 3:
            next_step(bot, chat_id, "You alread have 3 lists, you can't create more", 
                     choose_an_option, set_main_menu_keyboard())
            return

        next_step(bot, chat_id, f"*{user_name}, type a name of the list*", create_option_handler, remove_keyboard)

    elif message.text == "🔧 Delete":
        print("Delete")

    elif message.text == "🔑 Update":
        print("Update")

    elif message.text == "💎 Set time":
        print("Set time")


def create_option_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    list_name = message.text
    same_list_id = UserListManager.is_there_same_list(list_name, user_id)

    if same_list_id is not None:
        error_message_text = "*You already have a list with the similar name*"
        next_step(bot, chat_id, error_message_text, remove_keyboard, create_option_handler)
        return    

    next_step(bot, chat_id, "Now write words for remembering", fill_words,
             remove_keyboard, list_name)


def fill_words(message, list_name):
    words = message.text
    chat_id = message.chat.id

    words_length = len(words)

    if words_length <= 5 or words_length >= 2500:
        error_message_text = "*There was error occured: You can not write more than 2500 and less than 5 symbols!*"
        next_step(bot, chat_id, error_message_text, remove_keyboard, set_time_format)
        return

    next_step(bot, chat_id, "*Select the time format for interval sending*", 
             set_time_format, set_time_format_keyboard(), list_name, words)


def set_time_format(message, list_name, words):
    next_step(bot, message.chat.id, f"How many {message.text} do you want to set", time_itself_set,
            remove_keyboard, message.text, list_name, words)


def time_itself_set(message, time_format, list_name, words):
    if time_format == "Minutes": # There was a dictionary with "time_format: to_multiply"
        to_multiply = 60         # But I've decided to overwrite this with if-elif statements due to perfomance's decreasing
    elif time_format == "Hours":
        to_multiply = 3600
    elif time_format == "Days":
        to_multiply = 86400
    elif time_format == "Weekends":
        to_multiply = 604800

    try: 
        time = int(message.text)
        time_in_seconds = time * to_multiply
    except Exception:
        next_step(bot, message.chat.id, "Unable to set the time, try again (Do not write letters while you're setting the time)",
                time_itself_set, remove_keyboard, time_format, list_name, words)
        return
    
    create_list(message, list_name, words, time_format, time_in_seconds)


def create_list(message, list_name, words, time_format, time):
    user_id = message.from_user.id

    #User's creation
    the_user = DbTools.get_fields_from_table('users', 'id', f'id = {user_id}')
    chat_id = message.chat.id

    if the_user is None:
        UserManager.add_user(user_id, 1)
    
    else:
        UserManager.increase_users_lists_count(user_id)
    
    UserListManager.add_list(user_id, list_name, words, time)

    bot.send_message(chat_id, "The list has succesfully been created!")

    next_step(bot, chat_id, "*Would you like to create/delete/update a list*",
            choose_an_option, set_main_menu_keyboard())


@bot.message_handler(commands=["start"])
def handle_start_message(message):
    chat_id = message.chat.id
 
    bot.send_message(chat_id, config.BOT_GREETING, parse_mode="markdown") 
    next_step(bot, chat_id, "*Would you like to create/delete/update a list*",
            choose_an_option, set_main_menu_keyboard())


bot.polling()