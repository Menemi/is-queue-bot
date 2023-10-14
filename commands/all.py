import logging
import sqlite3

import db_manager

from aiogram import Bot, Dispatcher, types
from config import token, path_to_db, menemi, menemi_com, chief_com, all_com

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher(bot)


def get_user(user_id: str):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    try:
        user = cursor.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'").fetchall()
        if len(user) == 0:
            return -1
        return user
    except sqlite3.IntegrityError:
        return


def check_group_chief_status(message: types.Message):
    user = get_user(message.from_user.id)
    if user == -1 or not user[0][2]:
        return False
    return True


async def check_users_group(message: types.Message):
    user = get_user(message.from_user.id)
    if user == -1 or user[0][3] == "XYYZ":
        await message.answer("Чтобы воспользоваться командами ты должен состоять в какой-то группе (/setgroup)\n"
                             "Твоя нынешняя группа: XYYZ")
        return False
    return True


def get_user_position(user_id: str):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    current_queue_name = get_user(user_id)[0][4]
    if current_queue_name != "temp":
        return cursor.execute(f"SELECT id FROM {current_queue_name} WHERE user_id = '{user_id}'").fetchall()[0][0]


# TODO: help
async def help(message: types.Message):
    answer = "\n".join(all_com)
    answer += "\n"

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    is_chief = cursor.execute(f"SELECT is_chief FROM users WHERE user_id = '{message.from_user.id}'").fetchall()[0][0]
    if is_chief:
        answer += "\n".join(chief_com)
        answer += "\n"

    if message.from_user.id == menemi:
        answer += "\n".join(menemi_com)
        answer += "\n"

    await bot.send_message(message.chat.id, answer, parse_mode="HTML")


# TODO: info
async def info(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    user = cursor.execute(f"SELECT * FROM users WHERE user_id = '{message.from_user.id}'").fetchall()[0]
    await bot.send_message(message.chat.id, f"user id: <code>{message.from_user.id}</code>\n"
                                            f"username: @{message.from_user.username.lower()}\n"
                                            f"group: <code>{user[3]}</code>\n"
                                            f"is group chief: <code>{user[2]}</code>\n"
                                            f"current queue: <code>{user[4]}</code>", parse_mode="HTML")


# TODO: set group
async def set_group(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    buttons = []
    groups = cursor.execute("SELECT name FROM groups").fetchall()
    for group in groups:
        buttons.append(types.InlineKeyboardButton(text=f"{group[0]}", callback_data=f"{group[0]}_select_group"))

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.answer(f"Выбери группу:", reply_markup=keyboard)


# TODO: select queue
async def select_queue(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    user = get_user(message.from_user.id)[0]

    if user[3] != "XYYZ":
        await message.answer(f"Твоя актуальная группа: <code>{user[3]}</code>\nЧтобы её поменять, обратись к @Menemi", parse_mode="HTML")
        return

    buttons = []

    tables_list = cursor.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'users' AND name NOT LIKE 'groups';").fetchall()
    is_queue_list_empty = True
    for table in tables_list:
        if message.from_user.id == menemi or table[0].__contains__(user[3]):
            is_queue_list_empty = False
            buttons.append(types.InlineKeyboardButton(text=f"{table[0]}", callback_data=f"{table[0]}_select_queue"))

    if is_queue_list_empty:
        await message.answer("Нет доступных для тебя очередей, попробуй создать новую: /newqueue")
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, "Выбери очередь", reply_markup=keyboard)
    return


# TODO: queue
async def queue(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    current_queue_name = get_user(message.from_user.id)[0][4]
    if current_queue_name != "temp":
        try:
            users = cursor.execute(
                f"SELECT * FROM {current_queue_name} WHERE user_id = '{message.from_user.id}'").fetchall()
            is_user_here = len(users)
            if is_user_here == 0:
                places = cursor.execute(f"SELECT id FROM {current_queue_name} WHERE user_id = '-'").fetchall()
                buttons = []
                for place in places:
                    buttons.append(types.InlineKeyboardButton(text=f"{place[0]}",
                                                              callback_data=f"{place[0]}_{current_queue_name}_select_place"))

                keyboard = types.InlineKeyboardMarkup(row_width=5)
                keyboard.add(*buttons)
                await bot.send_message(message.from_user.id, "Выбери очередь", reply_markup=keyboard)
            else:
                await message.answer(
                    f"Ты уже есть в очереди\nТвой номер в ней: {get_user_position(message.from_user.id)}")
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    else:
        await message.answer("Чтобы встать в очередь нужно сначала её выбрать: /selectqueue")


# TODO: list
async def list(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    current_queue_name = get_user(message.from_user.id)[0][4]
    if current_queue_name != "temp":
        try:
            users = cursor.execute(f"SELECT * FROM {current_queue_name}").fetchall()
            if len(users) == 0:
                await message.answer("Очередь пуста")
                return
            position = 1
            answer = f"{current_queue_name}:\n"
            for i in users:
                at = "" if i[2] == "-" else "@"
                answer += f"{position}. {at}{i[2]}\n"
                position += 1
            await message.answer(answer)
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    else:
        await message.answer("Сначала нужно выбрать очередь: /selectqueue")


# TODO: quit exit stop
async def quit(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    current_queue_name = get_user(message.from_user.id)[0][4]
    if current_queue_name != "temp":
        try:
            users = cursor.execute(
                f"SELECT * FROM {current_queue_name} WHERE user_id = '{message.from_user.id}'").fetchall()
            is_user_here = len(users)
            if is_user_here == 1:
                cursor.execute(
                    f"UPDATE {current_queue_name} SET user_id = '-', username = '-' WHERE id = {int(users[0][0])}")
                connection.commit()
                await message.answer("Ты вышел(-ла) из очереди, чтобы заново в неё встать, напиши команду: /queue")
            else:
                await message.answer("Тебя и так не было в очереди, не переживай :)")
        except sqlite3.IntegrityError:
            await message.answer("!ERROR!")
    else:
        await message.answer("Сначала нужно выбрать очередь: /selectqueue")


# TODO: new queue
async def new_queue(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    try:
        name = message.get_args().split(" ")
        if len(name) == 1:
            if name[0] == "":
                await message.answer("Чтобы создать очередь нужно указать её название через пробел")
                return

            user = get_user(message.from_user.id)[0]

            queue_name = f"{user[3]}_{name[0]}"

            queue_name = queue_name \
                .replace("`", "") \
                .replace("!", "") \
                .replace("@", "") \
                .replace("№", "") \
                .replace("#", "") \
                .replace(";", "") \
                .replace("$", "") \
                .replace("%", "") \
                .replace(":", "") \
                .replace("^", "") \
                .replace("&", "") \
                .replace("?", "") \
                .replace("*", "") \
                .replace("(", "") \
                .replace(")", "") \
                .replace("-", "") \
                .replace("—", "") \
                .replace("=", "") \
                .replace("+", "") \
                .replace("~", "") \
                .replace("\\", "") \
                .replace("|", "") \
                .replace("/", "") \
                .replace("\"", "") \
                .replace("\"", "") \
                .replace("}", "") \
                .replace("{", "") \
                .replace("[", "") \
                .replace("]", "") \
                .replace(",", "") \
                .replace(".", "") \
                .replace("<", "") \
                .replace(">", "")

            table = cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE type = 'table' AND name = '{queue_name}'").fetchall()
            if not table:
                db_manager.create_queue(queue_name)
                await message.answer(f"Очередь <code>{queue_name}</code> успешно создана", parse_mode="HTML")
                for i in range(30):
                    cursor.execute(f"INSERT INTO {queue_name}(user_id, username) VALUES(?,?)", ("-", "-"))
                    connection.commit()
                cursor.execute(
                    f"UPDATE users SET current_queue_name = '{queue_name}' WHERE user_id = {message.from_user.id};")
                connection.commit()
                return

            await message.answer(f"Очередь <code>{queue_name}</code> уже существует", parse_mode="HTML")
            cursor.execute(
                f"UPDATE users SET current_queue_name = '{queue_name}' WHERE user_id = {message.from_user.id};")
            connection.commit()
        else:
            await message.answer("Название очереди не должно содержать пробелов")
    except sqlite3.IntegrityError:
        return
