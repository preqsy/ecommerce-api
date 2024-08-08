FROM python:3.10-slim

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip && \
    pip install poetry

COPY . .

RUN poetry install --no-root


CMD ["poetry", "run", "pytest", "-vv"]