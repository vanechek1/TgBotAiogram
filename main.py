import mysql.connector
from mysql.connector import Error
from aiogram import Bot, Dispatcher, types, executor
import pymorphy2
from pymorphy2 import MorphAnalyzer
import os
from dotenv import load_dotenv
#
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher import FSMContext
#

# class Form(StatesGroup):
#     waiting_for_question = State()

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USERNAME = os.getenv("USERNAME")
USER_PASSWORD = os.getenv("USER_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
HOST_NAME = os.getenv("HOST_NAME")

bot = Bot(BOT_TOKEN)
# dp = Dispatcher(bot, storage=MemoryStorage())
dp = Dispatcher(bot)

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(host=HOST_NAME, user=USERNAME, passwd=USER_PASSWORD, database=DB_NAME)
        try:
            connection = mysql.connector.connect(host=HOST_NAME, user=USERNAME, passwd=USER_PASSWORD,database=DB_NAME)
        except Error as e: print(f"The error '{e}' occured")
    except Error as e: print(f"The error '{e}' occured")
    return connection

# def execute_query(connection, query):
#     with connection.cursor() as cursor:
#         try:
#             cursor.execute(query)
#             result = cursor.fetchall()
#             for i in range(len(result)):
#                 return result[0][i]
#         except Error as e: print(f"The error '{e}' occured")

def execute_query(connection, query, params=None):
    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            result = cursor.fetchall()  # Получаем все записи
            return result  # Возвращаем все записи
        except Error as e:
            print(f"The error '{e}' occurred")
            return []  # Возвращаем пустой список в случае ошибки

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Хочу задать вопрос')
    btn2 = types.KeyboardButton('Популярные вопросы')
    btn3 = types.KeyboardButton('Help')
    markup.add(btn1)
    markup.add(btn2, btn3)
    await message.reply('Привет! Я - бот-помощник, можешь задать мне вопрос, а я попробую на него ответить!', reply_markup=markup)

@dp.message_handler(text=['Популярные вопросы'])
async def popular(message: types.Message):
    # Список популярных вопросов достается из баз данных
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    btn1 = types.InlineKeyboardButton('Как не попасть в армию?', callback_data='q1')
    btn2 = types.InlineKeyboardButton('Проблемы с паролем "МойТиу"', callback_data='q2')
    btn3 = types.InlineKeyboardButton('Не пришла стипендия', callback_data='q3')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    await message.answer('Вот список популярных вопросов:', reply_markup=markup)

@dp.message_handler(text=['Хочу задать вопрос'])
async def question(message: types.Message):
    # Здесь должен быть поиск ключевого слова и обращение к базе данных
    await message.reply('Задай вопрос, а я попробую на него ответить')
    # await Form.waiting_for_question.set()

# @dp.message_handler(state=Form.waiting_for_question)
# async def askquestion(message: types.Message, state: FSMContext):
#     await message.reply(execute_query(create_connection(),"SELECT answer FROM information WHERE question LIKE '%арми%'"))
#     await state.finish()

@dp.message_handler(content_types=['text'])
async def askquestion(message: types.Message):
    if 'educon' in message.text:
        ans = execute_query(create_connection(), "SELECT * FROM information WHERE answer LIKE '%educon%'")
        if ans:
            markup = types.InlineKeyboardMarkup()  # количество кнопок в ряду
            for record in ans:
                question_id, question, answer = record
                markup.add(types.InlineKeyboardButton(f'{question}', callback_data=f'question_{question_id}'))
            await message.reply('Выберите вопрос из списка:', reply_markup=markup)
        else:
            response = "Записей с 'educon' не найдено."
            await message.reply(response)
        # await message.reply(execute_query(create_connection(), "SELECT * FROM information WHERE answer LIKE '%educon%'"))
        # await message.reply(execute_query(create_connection(),"SELECT answer FROM information WHERE question LIKE '%educon%'"))
    elif 'арми' in message.text:
        await message.reply(execute_query(create_connection(),"SELECT answer FROM information WHERE question LIKE '%арми%'"))
    else:
        await message.reply('Я не понимаю, чего вы хотите')

@dp.callback_query_handler(lambda c: c.data.startswith('question_'))
async def process_question(callback_query: types.CallbackQuery):
    question_id = str(callback_query.data.split('_')[1])
    ans = execute_query(create_connection(), "SELECT answer FROM information WHERE id = "+str(question_id))
    await callback_query.message.answer(ans[0][0])

@dp.callback_query_handler(lambda c: c.data in ['q1','q2','q3'])
async def popularQuestions(call: types.callback_query):
    if call.data=='q1':
        await bot.answer_callback_query(call.id)
        # Здесь из базы данных достается ответ
        await bot.send_message(call.from_user.id, 'Чтобы не попасть в армию, обратитесь в кабинет 120 1-го корпуса ТИУ на ул.Володарского, 38')
    elif call.data=='q2':
        await bot.answer_callback_query(call.id)
        # Здесь из базы данных достается ответ
        await bot.send_message(call.from_user.id, 'Попробуйте изменить пароль, нажав на кнопку "изменить пароль"')
    elif call.data=='q3':
        await bot.answer_callback_query(call.id)
        # Здесь из базы данных достается ответ
        await bot.send_message(call.from_user.id, 'Стипендия приходит 28-го числа каждого месяца. Если 28-ое выпадает на выходной день, то в ближайшую пятницу.')

@dp.message_handler(commands=['inline'])
async def info(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2) # количество кнопок в ряду
    markup.add(types.InlineKeyboardButton('Site', callback_data='сайта нет'))
    markup.add(types.InlineKeyboardButton('Hello', callback_data='hello'))
    await message.reply('Hello', reply_markup=markup)

# @dp.callback_query_handler(lambda c: c.data in ['question'])
# async def callback(call: types.CallbackQuery):
#     if call.data == 'question':
#         await bot.answer_callback_query(call.id)
#         await bot.send_message(call.from_user.id, 'Хороший вопрос, подумай сам')
#

# @dp.callback_query_handler()
# async def callback(call):
#     await call.message.answer(call.data)

create_connection()

executor.start_polling(dp)
