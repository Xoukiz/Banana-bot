import telebot
from telebot import types

# === НАСТРОЙКИ ===
BOT_TOKEN = '8683196707:AAGmLk8T7ctX5qanMA6IGHbrqtqdz0jD9J8'
CHANNEL_ID = -1004494162051
ADMIN_ID = 7068405868

bot = telebot.TeleBot(BOT_TOKEN)

pending_messages = {}

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID and message.chat.type == 'private')
def handle_user_message(message):
    user_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name

    markup = types.InlineKeyboardMarkup()
    btn_publish = types.InlineKeyboardButton('✅ Опубликовать', callback_data=f'pub_{user_id}')
    btn_reject = types.InlineKeyboardButton('❌ Отклонить', callback_data=f'rej_{user_id}')
    markup.add(btn_publish, btn_reject)

    pending_messages[user_id] = {
        'text': message.text or message.caption or '[медиа]',
        'message_id': message.message_id,
        'chat_id': user_id
    }

    bot.send_message(
        ADMIN_ID,
        f'📩 Новое сообщение от @{username} (ID: {user_id}):\n\n{message.text or "[медиа]"}',
        reply_markup=markup
    )

    bot.send_message(user_id, '✅ Сообщение отправлено на модерацию.')

@bot.callback_query_handler(func=lambda call: call.data.startswith(('pub_', 'rej_')))
def handle_moderation(call):
    action, user_id = call.data.split('_')
    user_id = int(user_id)

    if user_id not in pending_messages:
        bot.answer_callback_query(call.id, 'Сообщение уже обработано.')
        return

    msg_data = pending_messages[user_id]

    if action == 'pub':
        try:
            bot.send_message(CHANNEL_ID, msg_data['text'])
            bot.edit_message_text(
                f'✅ Опубликовано:\n\n{msg_data["text"]}',
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )
            bot.send_message(user_id, '✅ Ваше сообщение опубликовано!')
        except Exception as e:
            bot.send_message(ADMIN_ID, f'❌ Ошибка публикации: {e}')
    else:
        bot.edit_message_text(
            f'❌ Отклонено:\n\n{msg_data["text"]}',
            chat_id=ADMIN_ID,
            message_id=call.message.message_id
        )
        bot.send_message(user_id, '❌ Ваше сообщение отклонено.')

    del pending_messages[user_id]
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()
