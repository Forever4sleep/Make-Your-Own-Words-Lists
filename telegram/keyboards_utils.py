from telebot import types
from functions_wrapps import next_step


def set_time_format_keyboard():
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


def set_main_menu_keyboard(): 
    """Returns main menu's keyboard"""

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.row(
        types.KeyboardButton("🎲 Create"),
        types.KeyboardButton("🔧 Delete"),
    )
    markup.row(
        types.KeyboardButton("🔑 Update"),
        types.KeyboardButton("💎 Set time"),
    )

    return markup
    # if is_it_start_command: 
    #     next_step(bot, chat_id, "*Would you like to create a list or something else? Menu is below.*", 
    #             next_function, markup)
    # else:
    #     next_step(bot, chat_id, "*What do you want to do?*", next_function, markup)