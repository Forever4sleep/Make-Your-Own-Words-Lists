import sys
sys.path.insert(0, '../')

from telebot import TeleBot, types
import config

from db_utils.database_manage import UsersLists

bot = TeleBot(config.BOT_TOKEN)


def set_main_menu_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.row(
        types.KeyboardButton("🎲 Create"),
        types.KeyboardButton("🔧 Delete"),
    )
    markup.row(
        types.KeyboardButton("🔑 Update"),
        types.KeyboardButton("💎 Set time"),
    )

    offer_message = bot.send_message(chat_id, "*Would you like to create a list or something else? Menu is below.*", 
                    parse_mode="markdown", reply_markup=markup)
    
    bot.register_next_step_handler(offer_message, choose_an_option)


def choose_an_option(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    markup = types.ReplyKeyboardRemove(selective=False)

    if message.text == "🎲 Create":
        list_name = bot.send_message(chat_id, f'{user_name}, type a name of the list', 
                    reply_markup=markup)
        bot.register_next_step_handler(list_name, create_option_handler)

    elif message.text == "🔧 Delete":
        print("Delete")

    elif message.text == "🔑 Update":
        print("Update")

    elif message.text == "💎 Set time":
        print("Set time")

    print("End")


def create_option_handler(message):
    user_id = message.from_user.id
    list_name = message.text
    same_list_id = UsersLists.is_there_same_list(list_name, user_id)
    chat_id = message.chat.id

    if same_list_id is not None:
        error_message = bot.send_message(chat_id, "*You already have a list with the similar name*",
                                        parse_mode="markdown")
        
        bot.register_next_step_handler(error_message, create_option_handler)
        return
    

    words_message = bot.send_message(chat_id, "*Now write words for remembering*", parse_mode="markdown")
    bot.register_next_step_handler(words_message, create_list_with_words, list_name)


def create_list_with_words(message, list_name):
    # ! TODO: to implement the further logic of a list creation


@bot.message_handler(commands=["start"])
def handle_start_message(message):
    bot.send_message(message.chat.id, config.BOT_GREETING, parse_mode="markdown")
    set_main_menu_keyboard(message.chat.id)


bot.polling()