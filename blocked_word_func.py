from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery, Message, Photo
from pyrogram import Client, filters
import os
from data_base_users import DB_poll

api_id = os.getenv('ID_TG')
api_hash = os.getenv('HASH_TG')
bot_token = os.getenv('TOKEN_TG')

app = Client("mrga", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
GROUP = 'MakeRussiaGreatAgain_official'

# Блок запрещенных слов и ответ на любое сообщение
@app.on_message(filters.text & filters.chat(GROUP))
def blocked_word(app: Client, message: Message):
    word_black_list = []
    with open('blacklist.txt', encoding='utf-8') as f:
        for word in f:
            word = word.replace('\n', '')
            word_black_list.append(word)
    for dword in word_black_list:
        if message.text.lower().find(dword) != -1:
            app.delete_messages(message.chat.id, message.id)
            message.reply_text('Присутствуют запрещенные слова!')
            app.send_photo(message.chat.id,
                           "AgACAgIAAxkBAAPEY-F5nFLZxbtlK-skV19_uqGqLnUAAkXIMRt3VBFLilZPp1oXBlsACAEAAwIAA20ABx4E")
            return
    return False