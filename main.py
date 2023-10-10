import asyncio
import logging
import sqlite3

import db_manager

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from commands.all import check_users_group, new_queue, info, set_group, queue, list, select_queue, quit, help
from commands.chief import drop_queue, reset
from commands.menemi import update_chief_status, add_group, remove_group
from config import token, path_to_db

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher(bot)


def register(message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    try:
        cursor.execute(f"SELECT * FROM users WHERE user_id='{message.from_user.id}'")
        user_count = len(cursor.fetchall())
        if user_count == 0:
            cursor.execute("INSERT INTO users(user_id, username) VALUES(?,?)",
                           (message.from_user.id, message.from_user.username.lower()))
            connection.commit()
        else:
            cursor.execute(f"SELECT * FROM users WHERE username='{message.from_user.username.lower}'")
            user_count = len(cursor.fetchall())
            if user_count == 0:
                cursor.execute(
                    f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
                connection.commit()
            return
    except Exception:
        return


async def check_group(message):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    group = cursor.execute(f"SELECT * FROM users WHERE user_id = '{message.from_user.id}'").fetchall()[0][3]
    if group == "XYYZ":
        await set_group_command(message)


@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    register(message)
    await check_group(message)
    if await check_users_group(message):
        await help_command(message)


@dp.message_handler(commands="help")
async def help_command(message: types.Message):
    register(message)
    await check_group(message)
    await help(message)


@dp.message_handler(commands="info")
async def info_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await info(message)


@dp.message_handler(commands="queue")
async def queue_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await queue(message)


@dp.message_handler(commands=["quit", "exit", "stop"])
async def quit_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await quit(message)


@dp.message_handler(commands="list")
async def list_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await list(message)


@dp.message_handler(commands="newqueue")
async def new_queue_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await new_queue(message)


@dp.message_handler(commands="selectqueue")
async def select_queue_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await select_queue(message)


@dp.message_handler(commands="dropqueue")
async def drop_queue_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await drop_queue(message)


@dp.message_handler(commands="setgroup")
async def set_group_command(message: types.Message):
    await set_group(message)


@dp.message_handler(commands="updchief")
async def upd_chief_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await update_chief_status(message)


@dp.message_handler(commands="reset")
async def reset_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await reset(message)


@dp.message_handler(commands="addgroup")
async def add_group_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await add_group(message)


@dp.message_handler(commands="removegroup")
async def remove_group_command(message: types.Message):
    register(message)
    await check_group(message)

    if not await check_users_group(message):
        return
    await remove_group(message)


@dp.callback_query_handler(Text(endswith="_select_queue"))
async def callbacks_select_place(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    data = data.replace("_select_queue", "")
    cursor.execute(f"UPDATE users SET 'current_queue_name' = '{data}' WHERE user_id = '{user_id}'")
    connection.commit()

    await call.message.edit_text(f"Ты выбрал очередь: <code>{data}</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query_handler(Text(endswith="_drop_queue"))
async def callbacks_select_place(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    data = data.replace("_drop_queue", "")
    db_manager.drop_queue(data)
    cursor.execute(f"UPDATE users SET 'current_queue_name' = 'temp' WHERE current_queue_name = '{data}'")
    connection.commit()

    await call.message.edit_text(f"Ты удалил очередь: <code>{data}</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query_handler(Text(endswith="_select_group"))
async def callbacks_select_place(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    data = data.replace("_select_group", "")
    cursor.execute(f"UPDATE users SET 'group' = '{data}' WHERE user_id = {user_id};")
    connection.commit()

    await call.message.edit_text(f"Ты выбрал группу: <code>{data}</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query_handler(Text(endswith="_select_place"))
async def callbacks_select_place(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id
    username = call.from_user.username
    data = data.replace("_select_place", "")
    queue_name = data[data.index("_") + 1:]
    place = data.split("_")[0]

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(f"UPDATE {queue_name} SET user_id = '{user_id}', username = '{username}' WHERE id = {int(place)}")
    connection.commit()

    await call.message.edit_text(f"Твой номер в очереди: <code>{place}</code>", parse_mode="HTML")
    await call.answer()


@dp.callback_query_handler(Text(endswith="_remove_group"))
async def callbacks_select_place(call: types.CallbackQuery):
    data = call.data

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    data = data.replace("_remove_group", "")
    cursor.execute(f"DELETE FROM groups WHERE name = '{data}'")
    connection.commit()

    await call.message.edit_text(f"Ты удалил группу: <code>{data}</code>", parse_mode="HTML")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
