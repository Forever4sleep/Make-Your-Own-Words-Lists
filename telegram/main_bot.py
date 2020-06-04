import sys
sys.path.insert(0, '../')

from telebot import TeleBot, types
import config
import datetime

from db_utils.database_manage import UserManager, UserListManager, DbTools

bot = TeleBot(config.BOT_TOKEN)

remove_keyboard = types.ReplyKeyboardRemove(False)

# ! From the first view, it may be scary to read the code, but the majority of the code is just linked functions that are responsible for lists' creation

#Keyboards

def set_time_format_keyboard(chat_id):
    """Sets the time format selecting's keyboard"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    markup.row(
        types.KeyboardButton("Minutes"),
        types.KeyboardButton("Hours"),
    )
    markup.row(
        types.KeyboardButton("Days"),
        types.KeyboardButton("Weekends")
    )

    return markup


def set_main_menu_keyboard(chat_id, is_it_start_command=True): 
    """Sets the main menu's keyboard, executing next step function optionally"""

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.row(
        types.KeyboardButton("🎲 Create"),
        types.KeyboardButton("🔧 Delete"),
    )
    markup.row(
        types.KeyboardButton("🔑 Update"),
        types.KeyboardButton("💎 Set time"),
    )

    if is_it_start_command: 
        next_step(chat_id, "*Would you like to create a list or something else? Menu is below.*", 
                choose_an_option, markup)
    else:
        next_step(chat_id, "*What do you want to do?*", choose_an_option, markup)


def choose_an_option(message):
    """A function that sets a furhter action"""
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    if message.text == "🎲 Create":
        next_step(chat_id, f"{user_name}, type a name of the list", create_option_handler, remove_keyboard)

    elif message.text == "🔧 Delete":
        print("Delete")

    elif message.text == "🔑 Update":
        print("Update")

    elif message.text == "💎 Set time":
        print("Set time")


def next_step(chat_id, message, handler_func, markup, *args, **kwargs):
    """
    
    A wrap for bot.register_next_step_handler
    It may be used for case if user inputs wrong data and need to repeat same function use this
    
    """

    msg = bot.send_message(chat_id, message, parse_mode='markdown', reply_markup=markup)
    bot.register_next_step_handler(msg, handler_func, *args, **kwargs)


def create_option_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    list_name = message.text
    same_list_id = UserListManager.is_there_same_list(list_name, user_id)

    if same_list_id is not None:
        error_message_text = "*You already have a list with the similar name*"
        next_step(chat_id, error_message_text, remove_keyboard, create_option_handler)
        return    

    next_step(chat_id, "Now write words for remembering", fill_words,
             remove_keyboard, list_name)


def fill_words(message, list_name):
    words = message.text
    chat_id = message.chat.id

    words_length = len(words)

    if words_length <= 5 or words_length >= 2500:
        error_message_text = "*There was error occured: You can not write more than 2500 and less than 5 symbols!*"
        next_step(message.chat.id, error_message_text, remove_keyboard, set_time_format)
        return

    next_step(message.chat.id, "*Select the time format for interval sending*", 
             set_time_format, set_time_format_keyboard(chat_id), list_name, words)


def set_time_format(message, list_name, words):
    next_step(message.chat.id, f"How many {message.text} do you want to set", time_itself_set,
            remove_keyboard, message.text, list_name, words)


def time_itself_set(message, time_format, list_name, words):
    time_format_choices = { #Here's a dictionary, the values of each key is a value that time will be multipled on
        "Minutes": 60,
        "Hours": 3600,
        "Days": 86400 ,
        "Weekends": 604800,
    }

    try: 
        time = int(message.text)
        time_in_seconds = time * choices[time_format]
    except Exception:
        next_step(message.chat.id, "Unable to set the time, try again (Do not write letters while you're setting the time)",
                time_itself_set, remove_keyboard, time_format, list_name, words)
        return
    
    create_list(message, list_name, words, time_format, time_in_seconds)


def create_list(message, list_name, words, time_format, time):
    user_id = message.from_user.id

    #User's creation
    the_user = DbTools.get_fields_from_table('users', 'id', f'id = {user_id}')
    chat_id = message.chat.id

    if the_user is None:
        UserManager.add_user(user_id)
    
    UserListManager.add_list(user_id, list_name, words, time)

    bot.send_message(chat_id, "The list has succesfully been created!")
    set_main_menu_keyboard(chat_id, False)


@bot.message_handler(commands=["start"])
def handle_start_message(message):
    bot.send_message(message.chat.id, config.BOT_GREETING, parse_mode="markdown")
    set_main_menu_keyboard(message.chat.id, True)


bot.polling()