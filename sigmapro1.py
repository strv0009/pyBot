 
import asyncio
from aiogram import Router, Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from environs import Env
from aiogram.types import *
from aiogram.filters import *
import shutil
from DBhelper import *


env = Env()
env.read_env(".env")
token = ""
bot = Bot(token=token)
dp = Dispatcher()
router = Router()

values = {"login": "", "pass": "", "hwid": "", "ip": "", "version": "", "time_start": "", "time_end": ""}
chvalues = {"ch_login": "", "ch_pass": "", "time_end": ""}

row1 = [[InlineKeyboardButton(text="Добавить", callback_data="called_button_add")], [InlineKeyboardButton(text="Удалить", callback_data="called_button_del")], [InlineKeyboardButton(text="Изменить", callback_data="called_button_change")],[InlineKeyboardButton(text="Информация пользователя", callback_data="called_button_info")]]
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=row1)

@router.message(Command(commands=["start"]))
async def start(message: Message):
        await message.answer("Вызовите меню командой /menu")


@router.message(Command(commands=["menu"]))
async def menu_button(message: Message):
    await message.answer("Выберите действие", reply_markup=inline_keyboard)

@router.callback_query()
async def clicked(callback: CallbackQuery):
    connection = Connection("sql/users.db")
    cursor = connection.cursor()
    helper = DBhelper(connection=connection, cursor=cursor, table="users")
    if callback.data == "called_button_add":
        await callback.message.answer("Отправьте информацию последовательно, используя команды:\n/login - логин\n/pass - пароль\n/hwid - hwid\n/ip - ip\n/ver - версия приложения\n/timest - время выдачи подписки\n/timeen - время завершения подписки")
        if values["hwid"] != "" and values["ip"] != "" and values["login"] != "" and values["pass"] != "" and values["version"] != "":
            helper.exec(f"INSERT INTO {helper.table} (login, password, hwid, lastIP, AppVer, timeStart, timeEnd) VALUES(?, ?, ?, ?, ?, ?, ?)", values["login"], values["pass"], values["hwid"], values["ip"], values["version"], values["time_start"], values["time_end"])
            await callback.message.answer("Пользователь успешно добавлен")
            values["hwid"] = ""
            values["ip"] = ""
            values["login"] = ""
            values["pass"] = ""
            values["time_end"] = ""
            values["time_start"] = ""
            values["version"] = ""
        else:
            await callback.message.answer("Одно из полей осталось незаполненым. Пожалуйста убедитесь во внесении всех данных")
    elif callback.data == "called_button_del":
        row = []
        try:
            users = helper.getAll()
            for i in range(len(users)):
                row.append([InlineKeyboardButton(text=users[i][0], callback_data=users[i][2])])
            if len(row) == 0:
                await callback.message.answer("таблица пуста")
            else:
                key = InlineKeyboardMarkup(inline_keyboard=row)
                await callback.message.answer("Выберите пользователя", reply_markup=key)
        except Error:
            await callback.message.answer("Возникла непредвиденная ошибка")
    elif callback.data == "called_button_change":
        await callback.message.answer("Отправьте информацию последовательно, используя команды:\n/chlogin - изменить login\n/chpass - изменить password\n/chtimeen - изменить время окончиня подписки")
        row = []
        try:
            users = helper.getAll()
            for i in range(len(users)):
                row.append([InlineKeyboardButton(text=users[i][0], callback_data=f"{users[i][2]}@CH@")])
            if len(row) == 0:
                await callback.message.answer("таблица пуста")
            else:
                key = InlineKeyboardMarkup(inline_keyboard=row)
                await callback.message.answer("Выберите пользователя", reply_markup=key)
        except Error:
            await callback.message.answer("Возникла непредвиденная ошибка")

    elif "@CH@" in callback.data:
        if chvalues["ch_login"] == "" or chvalues["ch_pass"] == "" and chvalues["time_end"] != "":
            await callback.message.answer("Все поля должны быть заполнены")
        else:
            helper.exec(f'UPDATE {helper.table} SET login = "{chvalues["ch_login"]}" WHERE hwid = "{callback.data[:callback.data.index("@")]}"')
            helper.exec(f'UPDATE {helper.table} SET password = "{chvalues["ch_pass"]}" WHERE hwid = "{callback.data[:callback.data.index("@")]}"')
            helper.exec(f'UPDATE {helper.table} SET timeEnd = "{chvalues["time_end"]}" WHERE hwid = "{callback.data[:callback.data.index("@")]}";')
            chvalues["ch_login"] = ""
            chvalues["ch_pass"] = ""
            chvalues["time_end"] = ""
            await callback.message.answer("Данные успешно изменены")
    elif callback.data == "called_button_info":
        row = []
        try:
            users = helper.getAll()
            for i in range(len(users)):
                row.append([InlineKeyboardButton(text=users[i][0], callback_data=f"{users[i][2]}@INFO@")])
            if len(row) == 0:
                await callback.message.answer("таблица пуста")
            else:
                key = InlineKeyboardMarkup(inline_keyboard=row)
                await callback.message.answer("Выберите пользователя", reply_markup=key)
        except Error:
            await callback.message.answer("Возникла непредвиденная ошибка")
    elif "@INFO@" in callback.data:
        data = helper.cursor.execute(f'SELECT * FROM {helper.table} WHERE hwid = "{callback.data[:callback.data.index("@")]}"').fetchall()
        await callback.message.answer(f"login: {data[0][0]}\npassword: {data[0][1]}\nhwid: {data[0][2]}\nlast ip: {data[0][3]}\napp version: {data[0][4]}\nsub start: {data[0][5]}\nsub end: {data[0][6]}")
    else:
        helper.exec(f"DELETE FROM {helper.table} WHERE hwid = ?", callback.data)
        await callback.message.answer(f"Пользователь успешно удален")


@router.message(Command(commands=["chlogin"]))
async def chlogin(message: Message):
    nlogin = message.text[message.text.index("n")+1:].strip()
    chvalues["ch_login"] = nlogin
    await message.answer("Поле new login успешно изменено")

@router.message(Command(commands=["chpass"]))
async def chpass(message: Message):
    npass = message.text[message.text.index("s")+2:].strip()
    chvalues["ch_pass"] = npass
    await message.answer("Поле new password успешно изменено")

@router.message(Command(commands=["chtimeen"]))
async def chtime(message: Message):
    chtime = message.text[message.text.index("n")+1:].strip()
    chvalues["time_end"] = chtime
    await message.answer("Поле time end успешно изменено")


@router.message(Command(commands=["login"]))
async def name(message: Message):
    login = message.text[message.text.index("n")+1:].strip()
    values["login"] = login
    await message.answer("Поле login успешно заполнено")

@router.message(Command(commands=["pass"]))
async def passw(message: Message):
    password = message.text[message.text.index("s")+2:].strip()
    values["pass"] = password
    await message.answer("Поле password успешно заполнено")

@router.message(Command(commands=["hwid"]))
async def hwid(message: Message):
    h = message.text[message.text.index("d")+1:].strip()
    values["hwid"] = h
    await message.answer("Поле hwid успешно заполнено")

@router.message(Command(commands=["ip"]))
async def ip(message: Message):
    i = message.text[message.text.index("p")+1:].strip()
    values["ip"] = i
    await message.answer("Поле ip успешно заполнено")

@router.message(Command(commands=["ver"]))
async def ver(message: Message):
    v = message.text[message.text.index("r")+1:].strip()
    values["version"] = v
    await message.answer("Поле version успешно заполнено")

@router.message(Command(commands=["timest"]))
async def timest(message: Message):
    st = message.text[message.text.index("s")+2:].strip()
    values["time_start"] = st
    await message.answer("Поле time start успешно сохранено")

@router.message(Command(commands=["timeen"]))
async def timeen(message: Message):
    en = message.text[message.text.index("n")+1:].strip()
    values["time_end"] = en
    await message.answer("Поле time end успешно сохранено")

async def main():
    dp.include_router(router=router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main=main())
