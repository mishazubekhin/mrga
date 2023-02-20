import asyncio
import sqlite3

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery, Message, \
    Photo
from pyrogram import Client, filters
import os

from blocked_word_func import blocked_word
from data_base_users import DB_poll

api_id = os.getenv('ID_TG')
api_hash = os.getenv('HASH_TG')
bot_token = os.getenv('TOKEN_TG')

app = Client("mrga", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
GROUP = 'MakeRussiaGreatAgain_official'

WELCOME_MESSAGE = 'Доступная демократия сейчас!\nЧтобы начать делать жизнь лучше нажмите /start'
WELCOME_MESSAGE_AFTER_START = '''
        Вы стали активным участником в жизни общества!\n
    Вам будут приходить голосования, запущенные такими же, как ты!\n 
    Чтобы выбрать свой регион, нажмите кнопку "Выбрать свой дом"\n
    Чтобы создать голосование в выбранном регионе, нажмите кнопку "Создать голосование"\n
    Чтобы вызвать своё голосование для контроля, нажмите кнопку "Мои петиции"\n
    Чтобы понять, ЧТО ВООБЩЕ ПРОИСХОДИТ, нажмите кнопку "Инструкция" 
    '''

WELCOME_MESSAGE_BUTTONS = [
    [InlineKeyboardButton('Выбрать свой дом', callback_data='choose_home')],
    [InlineKeyboardButton('Создать голосование', callback_data='create_universal_vote')]
    # [InlineKeyboardButton('Мои петиции', callback_data='my_petition')],
    # [InlineKeyboardButton('Инструкция', callback_data='tutorial')]
]


@app.on_message(filters.command('start'))
def welcome_start(app: Client, message: Message):
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute(f"INSERT OR IGNORE INTO polls (user_id) VALUES ('{message.from_user.id}')")
    db_vote.commit()
    db_vote.close()
    reply_markup = InlineKeyboardMarkup(WELCOME_MESSAGE_BUTTONS)
    message.reply(text=WELCOME_MESSAGE_AFTER_START, reply_markup=reply_markup, disable_web_page_preview=True)


region_list = []
with open('list_region_car.txt', encoding='utf-8') as file:
    for region in file:
        region = region.replace('\n', '')
        region_list.append(region)


@app.on_callback_query(group=5)
async def create_vote(app: Client, answer_message: CallbackQuery):
    if answer_message.data == 'create_universal_vote':
        await app.send_message(chat_id=answer_message.from_user.id, text=
        'Для создания петиции нажмите на команду /poll', reply_markup=None)
        return
    if answer_message.data == 'home':
        await answer_message.edit_message_text(text=WELCOME_MESSAGE_AFTER_START,
                                               reply_markup=InlineKeyboardMarkup(WELCOME_MESSAGE_BUTTONS),
                                               disable_web_page_preview=True)
        return


@app.on_callback_query(group=3)
async def choose_home(app: Client, answer_message: CallbackQuery):
    if answer_message.data == 'choose_home':
        MESSAGE_CHOOSE_REGION = 'Введите номер вашего региона!\nДля уточнения номера Вашего региона, нажмите кнопку ' \
                                '"Список регионов"'
        reply_choose_region = [
            [InlineKeyboardButton('Список регионов', url='https://www.consultant.ru/document/cons_doc_LAW_108669'
                                                         '/88a12659e7cc781c56303430d98ae6c8a683892a/')]
        ]
        await answer_message.edit_message_text(MESSAGE_CHOOSE_REGION,
                                               reply_markup=InlineKeyboardMarkup(reply_choose_region))

        @app.on_message(group=22)
        async def choose_region(app: Client, message: Message):
            if message.text in region_list:
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set region = ('{message.text}') WHERE user_id = ('{message.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                go_home = [
                    [InlineKeyboardButton('Вернуться на главную страницу', callback_data='home')],
                    [InlineKeyboardButton('Сменить регион', callback_data='choose_home')]
                    # добавить колбэк на возвращение
                ]
                await app.send_message(chat_id=answer_message.from_user.id,
                                       text='Прекрасно!\nТеперь ты сможешь участвовать в голосованиях своего региона!',
                                       reply_markup=InlineKeyboardMarkup(go_home))
                return
            else:
                await app.send_message(chat_id=answer_message.from_user.id, text='Еще нет такого региона!',
                                       reply_markup=InlineKeyboardMarkup(reply_choose_region))
                return
        return

@app.on_message(filters.command('poll'))
async def start_poll_creating(app: Client, message: Message):
    CREATE_POLL_MESSAGE = 'Изложите, пожалуйста, суть проблемы, согласно инструкции'
    reply_markup_tutorial = [
        [InlineKeyboardButton('Инструкция', url='https://t.me/MakeRussiaGreatAgain_official/7')]
        # поменять потом ссылку на инструкцию
    ]
    await app.send_message(chat_id=message.from_user.id, text=CREATE_POLL_MESSAGE,
                           reply_markup=InlineKeyboardMarkup(reply_markup_tutorial),
                           disable_web_page_preview=True)

    @app.on_message(filters.text, group=2)
    async def poll_creating(app: Client, message: Message):
        if blocked_word(app, message) is False:
            input_message = message.text
            msg_poll = await app.send_poll(chat_id=message.from_user.id, is_anonymous=False,
                                           question=input_message,
                                           options=['Согласен', "Возражаю",
                                                    "Не могу объективно оценить проблему"])
            msg_poll_id = msg_poll.id
            db_vote = sqlite3.connect("tguser.db")
            cur_vote = db_vote.cursor()
            cur_vote.execute(
                f"UPDATE polls set poll_id = ('{msg_poll_id}') WHERE user_id = ('{message.from_user.id}')")
            db_vote.commit()
            db_vote.close()
            CHECK_FOR_CORRECT = '''Проверьте, верно ли все, что вы хотели изложить?!\nДобавьте подтверждающие фотографии\nЕсли что-то неверно, продублируйте весь текст с учетом правок, нажав на кнопку "Хочу немного исправить!"'''
            CHECK_CORRECT_BUTTONS = [
                [InlineKeyboardButton('Добавить фотографию к петиции', callback_data='add_photo')],
                [InlineKeyboardButton('Все верно!', callback_data='all_right')],
                [InlineKeyboardButton('Хочу немного исправить!', callback_data='make_edit')]
            ]
            reply_markup_1 = InlineKeyboardMarkup(CHECK_CORRECT_BUTTONS)
            await app.send_message(chat_id=message.from_user.id, text=CHECK_FOR_CORRECT,
                                   reply_markup=reply_markup_1,
                                   disable_web_page_preview=True)

            @app.on_callback_query(group=2)
            async def improve_vote(app: Client, answer_message: CallbackQuery):
                if answer_message.data == 'all_right':
                    db_poll = DB_poll()
                    enum_user_id = db_poll.return_user_id()
                    ADD_PHOTO = [
                        [InlineKeyboardButton('На главную', callback_data='home')]
                    ]
                    reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
                    for id_user in enum_user_id:
                        await app.forward_messages(id_user, answer_message.from_user.id,
                                                   message_ids=db_poll.return_poll_id(
                                                       user_id=answer_message.from_user.id))
                        await app.send_photo(id_user, photo=db_poll.return_photos(
                            user_id=answer_message.from_user.id))
                    await app.send_message(message.from_user.id, 'Вернуться на главную',
                                           reply_markup=reply_markup_back_home,
                                           disable_web_page_preview=True)
                    return
                if answer_message.data == 'add_photo':
                    ADD_PHOTO = [
                        [InlineKeyboardButton('На главную', callback_data='home')]
                    ]
                    reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
                    await app.send_message(message.from_user.id, 'Добавьте одну или несколько актуальных фотографий!',
                                           reply_markup=reply_markup_back_home,
                                           disable_web_page_preview=True)

                    @app.on_message(filters.photo, group=2)
                    async def save_photos(app: Client, photo: Message):
                        db_vote = sqlite3.connect("tguser.db")
                        cur_vote = db_vote.cursor()
                        cur_vote.execute(
                            f"UPDATE polls set photos = ('{photo.photo.file_id}') WHERE user_id = ('{photo.from_user.id}')")
                        db_vote.commit()
                        db_vote.close()
                        # нужно добавить удаление полученного фото из чата
                        await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                        db_poll = DB_poll()
                        return_photo = db_poll.return_photos(user_id=answer_message.from_user.id)
                        CHECK_CORRECT_PHOTOS = [
                            [InlineKeyboardButton('Все верно!', callback_data='all_right')],
                            [InlineKeyboardButton('Хочу немного исправить!', callback_data='make_edit')]
                        ]
                        await app.forward_messages(answer_message.from_user.id, answer_message.from_user.id,
                                                   db_poll.return_poll_id(user_id=answer_message.from_user.id))
                        await app.send_photo(photo.from_user.id, return_photo,
                                             reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
                    return
                if answer_message.data == 'make_edit':
                    await app.send_message(chat_id=message.from_user.id, text='Введите заново полностью текст '
                                                                              'проблемы, с учетом правок!')
                    await poll_creating()
                    return
            return
        else:
            await app.send_message(chat_id=message.from_user.id, text=CREATE_POLL_MESSAGE)
            return



@app.on_message(filters.new_chat_members)
async def welcome_group(app: Client, message: Message):
    await message.reply_text(WELCOME_MESSAGE)
    await app.send_photo(message.chat.id,
                         'AgACAgIAAxkDAAKw3WPfpy7a5YEsMRzQiOXsc6drUyq7AALIxjEbuNIBS3f-tVfPSM5uAAgBAAMCAANtAAceBA')


# блок получения айди файлов
@app.on_message(filters.audio & filters.private)
async def get_id_audio(app: Client, message: Message):
    await message.reply(message.audio.file_id)


@app.on_message(filters.photo & filters.me, group=1)
async def get_id_photo(app: Client, message: Message):
    await message.reply(message.photo.file_id)


print('I`m working')
app.run()
