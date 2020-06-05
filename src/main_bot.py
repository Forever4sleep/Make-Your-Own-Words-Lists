import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import datetime
import time
import threading

from telebot import TeleBot, types, apihelper
from functools import wraps
from utils.db.database_manage import UserManager, UserListManager, DbTools
from utils.keyboards_utils import set_main_menu_keyboard, set_time_format_keyboard, set_removing_keyboard
from utils.functions_wrapps import next_step
from dateutil import parser

BOT = TeleBot(config.BOT_TOKEN)

REMOVE_KEYBOARD = types.ReplyKeyboardRemove(False) #It's created for not overusing types.ReplyKeyboardRemove in next_step


# ! From the first view, it may be scary to read the code, but the majority of one are just linked functions that are responsible for lists' creation/removing/updating and so on
# ! How it works? Firstly, when user starts the BOTwith '/start' command, 'handle_start_message' activates, then the main keyboard menu is being popped up 
# ! By executing 'next_step' and reply_markup=set_main_menu_keyboard, so, this is the principe how it works: Choosing an action, then following the further
# !  Instructions BOT gives to user


#An option selecting area


def choose_an_option(message):
    """A function that sets a further action"""
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    user_id = message.from_user.id

    if message.text == "🎲 Create":
        get_fields_from_users = DbTools.get_fields_from_table("users", "lists_count", f"id = {user_id}")

        lists_count = 0

        if get_fields_from_users:
            if get_fields_from_users[0][0] is not None:
                lists_count = get_fields_from_users[0][0]

        if lists_count >= 3:
            next_step(BOT, chat_id, "You alread have 3 lists, you can't create more", 
                     choose_an_option, set_main_menu_keyboard())
            return

        next_step(BOT, chat_id, f"*{user_name}, type a name of the list*", create_option_handler, REMOVE_KEYBOARD)

    elif message.text == "🔧 Delete":
        get_fields_from_lists = DbTools.get_fields_from_table("lists", "name", f"user_id = {user_id}")

        if get_fields_from_lists:
            next_step(BOT, chat_id, "*Choose a list*", delete_option_handler, set_removing_keyboard(get_fields_from_lists))
        else: 
           next_step(BOT, chat_id, "*You have no lists*", choose_an_option, set_main_menu_keyboard()) 
           return

    elif message.text == "🔑 Update":
        print("Update")

    elif message.text == "💎 Set time":
        print("Set time")


#Ending of selection area


#List removing area


def delete_option_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    list_name = message.text
    get_lists_name = DbTools.get_fields_from_table("lists", "name", f"name = '{list_name}' and user_id = {user_id}") 
    does_list_exist = get_lists_name is not None and get_lists_name[0] is not None
    
    if does_list_exist:
        UserListManager.remove_list(user_id, list_name)

        next_step(BOT, chat_id, "*The list has succesfully been deleted!*", choose_an_option, set_main_menu_keyboard())
        try:
            UserManager.interact_with_lists_count(user_id, "decrease")
        except Exception:
            print("Error Log: The user has 0 lists_count!")
    else:
        next_step(BOT, chat_id, "*You have no list with such name*", delete_option_handler, REMOVE_KEYBOARD)
        return



#Ending of list removing area


# List creation area


def create_option_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    list_name = message.text
    same_list_id = UserListManager.is_there_same_list(list_name, user_id)

    if same_list_id is not None:
        error_message_text = "*You already have a list with the similar name*"
        next_step(BOT, chat_id, error_message_text, REMOVE_KEYBOARD, create_option_handler)
        return    

    next_step(BOT, chat_id, "Now write words for remembering", fill_words,
             REMOVE_KEYBOARD, list_name)


def fill_words(message, list_name):
    words = message.text
    chat_id = message.chat.id

    words_length = len(words)

    if words_length <= 5 or words_length >= 2500:
        error_message_text = "*There was error occured: You can not write more than 2500 and less than 5 symbols!*"
        next_step(BOT, chat_id, error_message_text, REMOVE_KEYBOARD, set_time_format)
        return

    next_step(BOT, chat_id, "*Select the time format for interval sending*", 
             set_time_format, set_time_format_keyboard(), list_name, words)


def set_time_format(message, list_name, words):
    next_step(BOT, message.chat.id, f"How many {message.text} do you want to set", time_itself_set,
            REMOVE_KEYBOARD, message.text, list_name, words)


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
        next_step(BOT, message.chat.id, "Unable to set the time, try again (Do not write letters while you're setting the time)",
                time_itself_set, REMOVE_KEYBOARD, time_format, list_name, words)
        return
    
    create_list(message, list_name, words, time_format, time_in_seconds)


def create_list(message, list_name, words, time_format, time):
    user_id = message.from_user.id

    #User's creation
    the_user = DbTools.get_fields_from_table('users', 'id', f'id = {user_id}')
    chat_id = message.chat.id
    
    if not the_user:
        UserManager.add_user(user_id, 1)
    else:
        UserManager.interact_with_lists_count(user_id, "increase")
    
    UserListManager.add_list(user_id, list_name, words, time, chat_id)

    BOT.send_message(chat_id, "The list has succesfully been created!")

    next_step(BOT, chat_id, "*Would you like to create/delete/update a list*",
            choose_an_option, set_main_menu_keyboard())


#Ending of list creation area


#Sending words area


def send_words():
    while True:
        time.sleep(80)

        all_lists = DbTools.get_fields_from_table("lists", "*", "none")
        for field in all_lists:

            words = field[5]
            
            update_date = field[4]
            list_name = field[2]
            list_id = field[0]

            chat_id = field[1]
            
            sending_time = field[3]
            time_now = datetime.datetime.now()
            parsed_last_updated_time = parser.parse(str(update_date))

            if (time_now - parsed_last_updated_time).seconds >= sending_time:
                BOT.send_message(chat_id, f"*REMINDING OF {list_name}!*\n\n*{words}*", parse_mode="markdown")
                UserListManager.update_last_update_datetime(list_id)


#Ending of sending words area


@BOT.message_handler(commands=["start"])
def handle_start_message(message):
    chat_id = message.chat.id
 
    BOT.send_message(chat_id, config.BOT_GREETING, parse_mode="markdown") 
    next_step(BOT, chat_id, "*Would you like to create/delete/update a list*",
            choose_an_option, set_main_menu_keyboard())


threading.Thread(target=send_words).start()
BOT.polling(none_stop=True)