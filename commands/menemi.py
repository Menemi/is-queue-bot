import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from config import token, path_to_db, menemi
from commands.all import get_user, check_group_chief_status

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token)
dp = Dispatcher(bot)


# TODO: update chief status
async def update_chief_status(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    args = message.get_args().split(" ")
    if message.from_user.id == menemi:
        try:
            if len(args) != 2:
                await message.answer("Для выдачи роли старосты: [/updchief 433013981 1]")
                return

            user = get_user(args[0])
            if user == -1:
                await message.answer("Такого пользователя нет в системе")
                return
            if args[1] == "0" or args[1] == "1":
                cursor.execute(
                    f"UPDATE users SET is_chief = {args[1]} WHERE user_id = {args[0]};")
                connection.commit()
                await message.answer(f"@{user[0][1]} is_chief: {args[1]}")
            else:
                await message.answer("Для управления ролью пользователя нужно ввести либо 0, либо 1")
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    return


# TODO: add group
async def add_group(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    args = message.get_args().split(" ")
    if message.from_user.id == menemi:
        try:
            if (len(args) != 1) or (len(args) == 1 and args[0] == ""):
                await message.answer("Для добавления группы: [/addgroup M34041]")
                return

            group_name = cursor.execute(f"SELECT name FROM groups WHERE name = '{args[0]}'").fetchall()
            if not group_name:
                cursor.execute(f"INSERT INTO groups(name) VALUES(?)", (args[0],))
                connection.commit()
                await message.answer(f"Ты создал группу: <code>{args[0]}</code>", parse_mode="HTML")
            else:
                await message.answer("Такая группа уже есть")
            return
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    return


# TODO: remove group
async def remove_group(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    if message.from_user.id == menemi:
        try:
            groups = cursor.execute(f"SELECT name FROM groups").fetchall()
            buttons = []
            for group in groups:
                buttons.append(types.InlineKeyboardButton(text=f"{group[0]}", callback_data=f"{group[0]}_remove_group"))

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await bot.send_message(message.from_user.id, "Выбери какую группу удалить", reply_markup=keyboard)
            return
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    return
