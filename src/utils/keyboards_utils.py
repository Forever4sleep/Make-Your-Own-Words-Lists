from telebot import types
from utils.functions_wrapps import next_step
from utils.db.database_manage import DbTools


def set_time_format_keyboard():
    """Sets the time format selecting's keyboard"""

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

    markup.row (
        types.KeyboardButton("Minutes"),
        types.KeyboardButton("Hours"),
    )
    markup.row (
        types.KeyboardButton("Days"),
        types.KeyboardButton("Weekends")
    )
    markup.add(types.KeyboardButton("Main Menu"))

    return markup


def set_main_menu_keyboard(): 
    """Returns main menu's keyboard"""

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.row (
        types.KeyboardButton("🎲 Create"),
        types.KeyboardButton("🔧 Delete"),
    )

    return markup


def set_keyboard_with_lists(lists):
    """Returns removing keyboard"""

    names = [value[2] for value in lists]

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)

    markup.add(*[name for name in names])
    markup.add(types.KeyboardButton("Main Menu"))

    return markup