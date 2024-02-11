import sqlite3
from config import path_to_db

connection = sqlite3.connect(path_to_db)
cursor = connection.cursor()


def create_queue(name: str):
    cursor.execute(f"create table if not exists {name}"
                   " ("
                   "     id       INTEGER not null"
                   f"         constraint {name}_pk"
                   "             primary key autoincrement,"
                   "     user_id  TEXT not null,"
                   "     username TEXT not null"
                   " );")


def drop_queue(name):
    cursor.execute(f"drop table if exists {name}")


cursor.execute("create table if not exists users"
               "("
               "    user_id            TEXT                   not null"
               "        constraint users_pk"
               "            primary key,"
               "    username           TEXT    default 'None' not null,"
               "    is_chief           boolean default false  not null,"
               "    'group'            TEXT    default 'XYYZ' not null,"
               "    current_queue_name TEXT    default 'temp' not null"
               ");")

cursor.execute("create table if not exists groups"
               "("
               "    name TEXT default 'XYYZ' not null,"
               "    id   integer             not null"
               "        constraint groups_pk"
               "            primary key autoincrement"
               ");")
