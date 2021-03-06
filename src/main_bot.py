import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import datetime
import time
import threading

from telebot import TeleBot, types
from functools import wraps
from utils.db.database_manage import UserListManager, UserManager, DbTools
from utils.keyboards_utils import set_main_menu_keyboard, set_time_format_keyboard, set_keyboard_with_lists
from utils.functions_wrapps import next_step
from dateutil import parser


BOT = TeleBot(config.BOT_TOKEN)

REMOVE_KEYBOARD = types.ReplyKeyboardRemove(selective=False) #It's created for not overusing types.ReplyKeyboardRemove in next_step
BACK_BUTTON_MARKUP = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

BACK_BUTTON_MARKUP.add(types.KeyboardButton("Main Menu"))

BACK_BUTTON = BACK_BUTTON_MARKUP


# ! From the first view, it may be scary to read the code, but the majority of one are just linked functions that are responsible for lists' creation/removing
# ! How it works? Firstly, when user starts the BOT with '/start' command, 'handle_start_message' activates, then the main keyboard menu is being popped up 
# ! By executing 'next_step' and reply_markup=set_main_menu_keyboard, so, this is the principe how it works: Choosing an action, then following the further
# ! Instructions BOT gives to user


#Decorator for CACHED DB RESULTS filling area

def cache_results():
    def cache_results(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            func_result = func(*args, **kwargs)

            UserListManager.CACHED_LISTS_RESULTS = DbTools.get_fields_from_table(
                "lists", "*", "none"
            )

            UserManager.CACHED_USERS_RESULTS = DbTools.get_fields_from_table(
                "users", "*", "none"
            )

            if func_result is not None:
                return func_result

        return wrapped_func
    return cache_results


#Ending of the decorator's area


#Going to the main menu area


def go_to_main_menu(bot, chat_id, message=config.BOT_GREETING):
    next_step(bot, chat_id, message, choose_an_option, 
            set_main_menu_keyboard())


#Ending of going to the main menu area


#An option selecting area


def choose_an_option(message):
    """A function that sets a further action"""

    chat_id = message.chat.id
    user_name = message.from_user.first_name

    user_id = message.from_user.id

    option = message.text

    if option == "🎲 Create":
        get_fields_from_users = [lst for lst in UserManager.CACHED_USERS_RESULTS if lst[0] == user_id]
        
        lists_count = 0
        
        if get_fields_from_users and get_fields_from_users is not None:
            lists_count = get_fields_from_users[0][2]

        if lists_count >= 3:
            go_to_main_menu(BOT, chat_id, "You already have 3 lists, you can't create more")
            return

        next_step(BOT, chat_id, f"{user_name}, type a name of the list", create_option_handler, REMOVE_KEYBOARD)

    elif option == "🔧 Delete":
        get_fields_from_lists = [lst for lst in UserListManager.CACHED_LISTS_RESULTS if lst[1] == user_id]

        if get_fields_from_lists:
            markup = set_keyboard_with_lists(get_fields_from_lists)

            #The two arguments with the same values: first is for reply keyboard, second is for the further function
            next_step(BOT, chat_id, "Choose a list", delete_option_handler, markup, 
                     markup) 
        else: 
           go_to_main_menu(BOT, chat_id, "You have no lists") 
           return


#Ending of selection area


#List removing area


@cache_results()
def delete_option_handler(message, markup):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    list_name = message.text
    get_lists_name = [lst for lst in UserListManager.CACHED_LISTS_RESULTS if lst[2] == list_name and lst[1] == user_id]

    if get_lists_name:
        UserListManager.remove_list(user_id, list_name)

        go_to_main_menu(BOT, chat_id, "The list has succesfully been deleted!")
        UserManager.interact_with_lists_count(user_id, "decrease")

    elif list_name == "Main Menu":
        go_to_main_menu(BOT, chat_id)

    else:
        next_step(BOT, chat_id, "You have no list with such a name", delete_option_handler, markup, markup)
        return


#Ending of list removing area


# List creation area


def create_option_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    list_name = message.text
    same_list = [lst for lst in UserListManager.CACHED_LISTS_RESULTS if lst[2] == list_name and lst[1] == user_id]

    if same_list:
        error_message_text = "You already have a list with the similar name"
        next_step(BOT, chat_id, error_message_text, create_option_handler, REMOVE_KEYBOARD)
        return    

    next_step(BOT, chat_id, "Now write words for remembering", fill_words, BACK_BUTTON, list_name)


def fill_words(message, list_name):
    words = message.text
    chat_id = message.chat.id

    words_length = len(words)

    if words_length < 5 or words_length >= 2500:
        error_message_text = "There was error occured: You can not write more than 2500 and less than 5 symbols!"
        next_step(BOT, chat_id, error_message_text, fill_words,  REMOVE_KEYBOARD, list_name)
        return

    if words == "Main Menu":
        go_to_main_menu(BOT, chat_id)
        return
    
    #Getting rid of 'bad' symbols
    words = words.replace("'", " ")
    list_name = list_name.replace("'", " ")

    next_step(BOT, chat_id, "Select the time format for interval sending", 
             set_time_format, set_time_format_keyboard(), list_name, words)


def set_time_format(message, list_name, words):
    next_step(BOT, message.chat.id, f"How many {message.text} do you want to set", time_itself_set,
            REMOVE_KEYBOARD, message.text, list_name, words)


def time_itself_set(message, time_format, list_name, words):
    chat_id = message.chat.id

    if time_format == "Minutes": # There was a dictionary with "time_format: to_multiply"
        to_multiply = 60         # But I've decided to overwrite this with if-elif statements due to perfomance's decreasing
    elif time_format == "Hours":
        to_multiply = 3600
    elif time_format == "Days":
        to_multiply = 86400
    elif time_format == "Weekends":
        to_multiply = 604800
    elif time_format == "Main Menu":
        go_to_main_menu(BOT, chat_id)

    try: 
        time = int(message.text)
        
        if time < 5 and time_format == "Minutes":
            next_step(BOT, chat_id, "You can't set less than 5 minutes. Try one more time",
                time_itself_set, REMOVE_KEYBOARD, time_format, list_name, words)
            return

        time_in_seconds = time * to_multiply
    except Exception:
        next_step(BOT, chat_id, "Unable to set the time, try again (Do not write letters while you're setting the time)",
                time_itself_set, REMOVE_KEYBOARD, time_format, list_name, words)
        return
    else:
        create_list(message, list_name, words, time_format, time_in_seconds)


@cache_results()
def create_list(message, list_name, words, time_format, time):
    chat_id = message.chat.id

    #User's creation
    user_id = message.from_user.id
    the_user = [lst for lst in UserManager.CACHED_USERS_RESULTS if lst[0] == user_id]

    try:
        UserListManager.add_list(user_id, list_name, words, time, chat_id)

        if not the_user:
            UserManager.add_user(user_id, 1)
        else:
            UserManager.interact_with_lists_count(user_id, "increase")
    except Exception:
        go_to_main_menu(BOT, chat_id, "An error occured while list creating, try again")
        return        

    BOT.send_message(chat_id, "The list has succesfully been created!")

    go_to_main_menu(BOT, chat_id)


#Ending of list creation area


#Sending words area


def send_words():
    while True:
        
        time.sleep(350)

        all_lists = DbTools.get_fields_from_table("lists", "*", "none")

        for field in all_lists:

            words = field[5]
            
            list_update_date = field[4]
            list_name = field[2]
            list_id = field[0]

            chat_id = field[1]
            
            sending_time = field[3]
            time_now = datetime.datetime.now()
            parsed_last_updated_time = parser.parse(str(list_update_date))

            if (time_now - parsed_last_updated_time).seconds >= sending_time:          
                try: 
                    UserListManager.update_last_update_datetime(list_id)
                    BOT.send_message(chat_id, f"*🔥 REMINDING OF {list_name}!*\n\nWords:\n*{words}*", parse_mode="markdown")
                except:
                    print("Unable to send a message: the chat_id is not correct")
                    continue          


#Ending of sending words area


#Message handling area

@BOT.message_handler(commands=["start"])
def handle_start_message(message):
    chat_id = message.chat.id
 
    go_to_main_menu(BOT, chat_id)


#Ending of message handling area

threading.Thread(target=send_words).start()

BOT.enable_save_next_step_handlers(delay=10)

BOT.load_next_step_handlers()

BOT.polling(none_stop=True) 