from aiogram import (
    executor,
)

from handlers.chat_handlers import dp


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except Exception as err:
        print(err)
