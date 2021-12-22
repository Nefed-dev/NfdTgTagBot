#TgTaggerBot by Nefedov

Примененные библиотеки:
- aiogram
- SQLAlchemy
- asyncpg
- alembic

Бот с асинхронным взаимодействием с PostgreSQL, 

Перед стартом бота не забудь заполнить .env - файл, либо явяно указать следующиек переменные контейнеру:

POSTGRES_USER=

POSTGRES_PASSWORD=

POSTGRES_PORT=

POSTGRES_HOST=

POSTGRES_DB=

TG_TOKEN=



#### После старта контейнереров командой "docker-compose up --build" необходимо выполнить следующие 2 команды:
Генерация миграций из Моделей
1.     docker exec TgTagBot alembic revision --autogenerate -m "inits"

Применение миграций
2.     docker exec TgTagBot alembic upgrade head
