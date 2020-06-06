import telebot


def next_step(bot, chat_id, message, handler_func, markup, *args, **kwargs):
    """
    
    A wrap for bot.register_next_step_handler
    It may be used for case if user inputs wrong data and need to repeat same function use this
    bot - a TeleBot's instance
    handler_func - next function that'll be occured
    markup - kind of keyboard that'll be attached to message
    *args, **kwargs - additional args for handler_func

    """

    msg = bot.send_message(chat_id, f"*{message}*", parse_mode='markdown', reply_markup=markup)
    bot.register_next_step_handler(msg, handler_func, *args, **kwargs)