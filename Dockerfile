FROM python:3.10-slim


WORKDIR /usr/src/app


COPY poetry.lock pyproject.toml ./


RUN pip install --upgrade pip && \
    pip install poetry


COPY . .


RUN poetry install --no-root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
