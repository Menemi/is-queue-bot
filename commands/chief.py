import logging
import sqlite3
import db_manager

from aiogram import Bot, Dispatcher, types

from commands.all import get_user, check_group_chief_status
from config import token, path_to_db, menemi

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token)
dp = Dispatcher(bot)


# TODO: drop_queue
async def drop_queue(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    user = get_user(message.from_user.id)[0]
    if not check_group_chief_status(message) and message.from_user.id != menemi:
        return

    buttons = []

    tables_list = cursor.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'users' AND name NOT LIKE 'groups';").fetchall()
    is_queue_list_empty = True
    for table in tables_list:
        if message.from_user.id == menemi or table[0].__contains__(user[3]):
            is_queue_list_empty = False
            buttons.append(types.InlineKeyboardButton(text=f"{table[0]}", callback_data=f"{table[0]}_drop_queue"))

    if is_queue_list_empty:
        await message.answer("Нет доступных для тебя очередей, попробуй создать новую: /newqueue")
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, "Выбери очередь", reply_markup=keyboard)
    return


# TODO: reset
async def reset(message: types.Message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    current_queue_name = get_user(message.from_user.id)[0][4]
    if current_queue_name != "temp":
        if check_group_chief_status(message) or message.from_user.id == menemi:
            try:
                cursor.execute(f"UPDATE {current_queue_name} SET user_id = '-', username = '-' WHERE user_id != '-'")
                connection.commit()
                await message.answer(f"<code>{current_queue_name}</code> очищена", parse_mode="HTML")
            except sqlite3.IntegrityError:
                await message.answer("!ERROR!")
        return
