# syntax=docker/dockerfile:1.3.1
FROM python:3.9.9 as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


FROM base as builder
RUN apt update -y \
    && apt install --no-install-recommends -y \
        curl build-essential cmake libopenblas-dev liblapack-dev libjpeg-dev ssh git zip unzip

# POETRY installation
ENV POETRY_HOME=/etc/poetry \
    POETRY_VERSION=1.1.12 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# dependencies installation via POETRY
COPY ./pyproject.toml ./poetry.lock ./
RUN $POETRY_HOME/bin/poetry install --no-dev --no-root

FROM builder as development
RUN $POETRY_HOME/bin/poetry install --no-root
WORKDIR /app
COPY app ./app
COPY config ./config
EXPOSE 8000
CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "app.api:app"]

FROM base as production
COPY --from=builder /usr/local /usr/local
WORKDIR /app

ENV ENABLE_METRICS=true \
    VERSION=0.0.9 \
    GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/prj-aiml-pleb-vision-35429-f0732288bc52.json"
COPY app ./app
COPY config ./config
EXPOSE 8000

CMD uvicorn --host=0.0.0.0 --port=8000 --log-config config/logging.conf app.api:app