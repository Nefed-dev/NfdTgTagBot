FROM python:3.9.7-bullseye

ARG KV_ROOT_CA_SRC_URI

ENV \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.6

WORKDIR /usr/app/
COPY . /usr/app/

# install
RUN \
  echo "---> TimeZone: MSK" && \
    export TZ="Europe/Moscow" && \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && \
    date && \
  echo "---> Install poetry" && \
    curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python - && \
    ln -s "${HOME}"/.poetry/bin/poetry /usr/bin/poetry && \
    poetry config virtualenvs.create false && \
    poetry install && \
  echo "---> Cleaning up" && \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/*
#
#RUN \
#    cd usr/app && /
#    alembic upgrade head

#
#RUN \
#  echo "---> Alembic migrations" && \
#    alembic revision --autogenerate -m "Add models" && \
#    alembic upgrade head


CMD ["python3", "main.py"]
