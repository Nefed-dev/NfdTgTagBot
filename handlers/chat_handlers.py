from aiogram.types import (
    Message,
)
from aiogram.dispatcher.filters import Command
from db.dependencies import get_db_crud

from loader import dp


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
                f"/changetag - изменить юзернейм (старый, потом новый чз пробел)\n" \
                f"/deltag - удалить пользователя из БД"

    await message.answer(text=info_text)


@dp.message_handler(content_types=["new_chat_members"])
async def new_member(message: Message):
    """add new member in database (username-chat_id)"""
    user_tag = message.new_chat_members[0].username
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    await db.add_user(chat_id=chat_id, user_tag=user_tag)

    await message.answer(text=f'Участник доступен по тегу @{user_tag}')


@dp.message_handler(content_types=["left_chat_member"])
async def left_member(message: Message):
    user_name = message.left_chat_member.username
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    await db.delete_user_from_chat(chat_id=chat_id, user_tag=user_name)
    await message.answer(text=f'{user_name} покинул {chat_id}')


@dp.message_handler(Command('deltag'))
async def delete_user(message: Message):
    text = message.get_args()
    usernames = text.split(' ')
    chat_id = str(message.chat.id)
    db = await get_db_crud()
    for user_name in usernames:
        await db.delete_user_from_chat(chat_id=chat_id, user_tag=user_name)
    await message.answer(text=f'Удалена связка {usernames} и {chat_id}')


@dp.message_handler(Command("tagall"))
async def tag_all_member(message: Message):
    call_members = 'POWER RANGERS ПРИДИТЕ!!\n'
    chat_id = str(message.chat.id)
    db = await get_db_crud()
    all_members = await db.get_all_members_from_chat(
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

    db = await get_db_crud()
    await db.add_user(
        chat_id=chat_id,
        user_tag=user_tag
    )
    await message.answer(text=f'{user_tag} добавлен в БД')


@dp.message_handler(Command("addchat"))
async def add_chat(message: Message):
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    await db.add_chat(chat_id=chat_id)

    await message.answer(text='Чат добавлен в БД')


@dp.message_handler(Command("add"))
async def set_new_member(message: Message):
    chat_id = str(message.chat.id)
    users = message.get_args()
    users = users.split(' ')

    for user in users:
        if '@' in user:
            user = user.replace('@', '')
        db = await get_db_crud()
        await db.add_user(
            chat_id=chat_id,
            user_tag=user
        )
    await message.answer(text=f'Пользователь/ли были добавлены в базу: \n{users}')


@dp.message_handler(Command('setgroup'))
async def set_group_for_member(message: Message):
    chat_id = str(message.chat.id)

    info: str = message.get_args()
    info: list = info.split(" ")

    if len(info) < 2:
        await message.answer("Недостаточно данных. Введите {имя группы} {тег пользователя/ей}")
        return

    user_tags = info[1:]
    group_name = info[0]

    text = f'Следующим пользователям присвоена группа --{group_name}--:\n'
    for user_tag in user_tags:
        if '@' in user_tag:
            user_tag = user_tag.replace('@', '')
        db = await get_db_crud()
        await db.set_group_for_user_in_chat(
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

    db = await get_db_crud()

    if not group:
        group = 'nogroup'

    group_members = await db.get_members_by_group_from_chat(
        chat_id=chat_id,
        group=group
    )

    call_members: str = ''

    for member in group_members:
        call_members += f'@{member} '

    if not call_members:
        await message.answer(text='Group is empty or wrong group name')
        return

    await message.answer(text=call_members)


@dp.message_handler(Command('delgroup'))
async def delete_member_from_group(message: Message):
    chat_id = str(message.chat.id)
    info = message.get_args()

    db = await get_db_crud()

    await db.set_group_for_user_in_chat(
        chat_id__=chat_id,
        user_tag=info,
        group_='nogroup',
    )
    text: str = f'Удалена группа у {info}'
    await message.answer(text)


@dp.message_handler(Command('getgroups'))
async def get_group_list_for_chat(message: Message):
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    chat_groups = await db.get_groups_from_chat(
        chat_id=chat_id
    )
    text = f'Chat {chat_id} groups: '
    chat_groups = list(chat_groups)
    for group in sorted(chat_groups):
        text += f"\n▶ {group}"

    await message.answer(text)


@dp.message_handler(Command('changetag'))
async def change_username(message: Message):
    usernames = message.get_args()
    usernames = usernames.split(' ')
    if len(usernames) != 2:
        await message.answer('Необходимо передать только старый и новый Юзернейм через пробел!!!')
        return

    old_username, new_username = usernames

    db = await get_db_crud()
    await db.change_user_tag(
        old_user_tag=old_username,
        new_user_tag=new_username
    )
    await message.answer(f'Прошла смена юзернейма {old_username} -> {new_username} ')


@dp.message_handler(Command("addzoom"))
async def add_zoom(message: Message):
    chat_id = str(message.chat.id)

    info = message.get_args()
    zoom_addresses = info.split(' ')
    for zoom_address in zoom_addresses:
        db = await get_db_crud()
        await db.add_zoom_address(zoom_address=zoom_address, chat_id=chat_id)
    await message.answer(f'Zoom адрес добавилен: \n{zoom_addresses}')


@dp.message_handler(Command('zoom'))
async def get_zoom_links(message: Message):
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    message_text: str = "Zoom-Адрес(а):\n"
    zooms = await db.get_zoom_from_chat(
        chat_id=chat_id
    )
    for zoom in zooms:
        message_text += f"\n{zoom}"
    await message.answer(message_text)


@dp.message_handler(Command('delzoom'))
async def del_zoom_link(message: Message):
    chat_id = str(message.chat.id)

    info = message.get_args()
    zoom_address = info.strip()
    db = await get_db_crud()
    await db.delete_zoom_from_chat(zoom_address=zoom_address, chat_id=chat_id)
    await message.answer(text="Зум отвязан")


@dp.message_handler(Command('clearzoom'))
async def clear_zoom_from_chat(message: Message):
    chat_id = str(message.chat.id)

    db = await get_db_crud()
    await db.clear_zoom_chat(chat_id=chat_id)
    await message.answer(f'Все Zoom-ссылки отвязаны от чата')
