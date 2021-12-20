from aiogram import (
    Bot,
    Dispatcher,
    executor,
)
from aiogram.types import (
    Message,
)
from aiogram.dispatcher.filters import Command
from db import db_api as db
from config import settings_app

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


TG_TOKEN = settings_app.TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

DATABASE_URL = settings_app.dsn
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)


@dp.message_handler(Command("info"))
async def send_info(message: Message):
    info_text = f"🟢 TgTagBot by Nefedov\n\n" \
                f"/info - показать команды\n" \
                f"/tagall - тегнуть всех зарегистрированных\n" \
                f"/addchat - инициализировать чат\n" \
                f"/add - добавить пользователя(ей)\n" \
                f"/setgroup - добавить (изменить) пользователя(ей) в группу (сначала группу, потом пользователей)\n" \
                f"/taggroup - тегнуть группу\n" \
                f"/delgroup - удалить группу у пользователя\n" \
                f"/getgroups - получить список групп\n" \
                f"/changeusername - изменить юзернейм (старый, потом новый чз пробел)"

    await message.answer(text=info_text)


@dp.message_handler(content_types=["new_chat_members"])
async def new_member(message: Message):
    """add new member in database (username-chat_id)"""
    user_tag = message.new_chat_members[0].username
    chat_id = str(message.chat.id)

    await db.add_user(session=async_session, chat_id=chat_id, user_tag=user_tag)
    # сохранить в БД Юзернейм-чат

    await message.answer(text=f'Участник доступен по тегу @{user_tag}')


@dp.message_handler(content_types=["left_chat_member"])
async def left_member(message: Message):
    user_name = message.left_chat_member.username
    chat_id = str(message.chat.id)

    # Удалить из БД Юзернейм-чат
    await db.delete_user_from_chat(session=async_session, chat_id=chat_id, user_tag=user_name)
    await message.answer(text=f'{user_name} покинул {chat_id}')

@dp.message_handler(Command('deleteuser'))
async def delete_user(message: Message):
    text = message.get_args()
    usernames = text.split(' ')
    chat_id = str(message.chat.id)

    for user_name in usernames:
        await db.delete_user_from_chat(session=async_session, chat_id=chat_id, user_tag=user_name)
        await message.answer(text=f'{user_name} покинул {chat_id}')

@dp.message_handler(Command("tagall"))
async def tag_all_member(message: Message):
    call_members = 'POWER RANGERS ПРИДИТЕ!!\n'

    chat_id = str(message.chat.id)

    all_members = await db.get_all_members_from_chat(
        session=async_session,
        chat_id=chat_id,
    )

    if not all_members:
        await message.answer(text='Некого вызывать')
    for member in all_members:
        call_members += f' @{member}'
    await message.answer(text=call_members)


@dp.message_handler(Command("addme"))
async def add_me(message: Message):
    chat_id = str(message.chat.id)

    user_tag = message.from_user.username
    await db.add_user(
        session=async_session,
        chat_id=chat_id,
        user_tag=user_tag
    )


@dp.message_handler(Command("addchat"))
async def add_chat(message: Message):
    chat_id = str(message.chat.id)

    print(chat_id)
    await db.add_chat(
        session=async_session,
        chat_id=chat_id
    )
    await message.answer(text='Чат добавлен в БД')


@dp.message_handler(Command("add"))
async def set_new_member(message: Message):
    chat_id = str(message.chat.id)
    users = message.get_args()
    users = users.split(' ')
    for user in users:
        if '@' in user:
            user = user.replace('@', '')
        await db.add_user(
            session=async_session,
            chat_id=chat_id,
            user_tag=user
        )
    await message.answer(text=f'Пользователь/ли были добавлены в базу: \n{users}')


@dp.message_handler(Command('setgroup'))
async def set_group_for_member(message: Message):
    chat_id = str(message.chat.id)

    info: str = message.get_args()
    info: list = info.split(" ")
    user_tags = info[1:]
    group_name = info[0]
    text = f'Следующим пользователям присвоена группа --{group_name}--:\n'
    for user_tag in user_tags:
        if '@' in user_tag:
            user_tag = user_tag.replace('@', '')
        await db.set_group_for_user_in_chat(
            session=async_session,
            chat_id__=chat_id,
            user_tag=user_tag,
            group_=group_name,
        )
        text += f'{user_tag} '
    await message.answer(text)


@dp.message_handler(Command("taggroup"))
async def tag_by_group_in_chat(message: Message):
    chat_id = str(message.chat.id)

    group = message.get_args()
    if not group:
        group = 'null'
    group_members = await db.get_members_by_group_from_chat(
        session=async_session,
        chat_id=chat_id,
        group=group
    )
    call_members: str = ''
    for member in group_members:
        call_members += f'@{member} '
    if not call_members:
        await message.answer(text='Group is empty or wrong group name')
    await message.answer(text=call_members)


@dp.message_handler(Command('delgroup'))
async def delete_member_from_group(message: Message):
    chat_id = str(message.chat.id)
    info = message.get_args()
    await db.set_group_for_user_in_chat(
        session=async_session,
        chat_id__=chat_id,
        user_tag=info,
        group_='null',
    )
    text: str = f'Удалена группа у {info}'
    await message.answer(text)


@dp.message_handler(Command('getgroups'))
async def get_group_list_for_chat(message: Message):
    chat_id = str(message.chat.id)

    chat_groups = await db.get_groups_from_chat(
        session=async_session,
        chat_id=chat_id
    )
    text = f'Chat {chat_id} groups: '
    chat_groups = list(chat_groups)
    for group in sorted(chat_groups):
        text += f"\n▶ {group}"

    await message.answer(text)


@dp.message_handler(Command('changeusername'))
async def change_username(message: Message):
    usernames = message.get_args()
    usernames = usernames.split(' ')
    if len(usernames) != 2:
        await message.answer('Необходимо передать только старый и новый Юзернейм через пробел!!!')
    old_username, new_username = usernames
    await db.change_user_tag(
        session=async_session,
        old_user_tag=old_username,
        new_user_tag=new_username
    )


# https://t.me/+zEDqI5JwVZ8xZWJi
if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except Exception as err:
        print(err)
