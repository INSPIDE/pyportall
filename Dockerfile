FROM python:3.8.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -m api && mkdir /app && chown api:api /app

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

USER api

COPY . .
