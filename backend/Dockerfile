FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false


COPY . .

RUN poetry install --with dev

CMD uvicorn src.main:app --host 0.0.0.0 --port 9999