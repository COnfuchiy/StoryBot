import telebot

from source.NAW.modules.NAWActions import NAWActions as Actions


# create bot
bot = telebot.TeleBot("1119352644:AAE6EHDtw0pX8fS0A2zLpBTboWKANm6jbjw")
game = Actions(bot)

# get main message
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == '/start':
        game.start_game(message.from_user.id)
    elif message.text == '/version':
        game.get_version(message.from_user.id)
    elif message.text.split(' ')[0]=='/shortcut':
        game.shortcut(message.from_user.id, message.text.split(' ')[1])
    else:
        game.handle_message(message.from_user.id,message.text)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data != '-1':
        if len(call.data.split('.'))==2:
            game.callback_next(call.message.chat.id,call.data, call.message.json['reply_markup']['inline_keyboard'][0],call.message.message_id)
        else:
            game.callback_pang(call.message.chat.id,call.message.message_id,call.data,call.message.json['reply_markup']['inline_keyboard'])


# set listen
bot.polling(none_stop=True, interval=0)