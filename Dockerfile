FROM python:3.10.8-alpine3.16

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN apk add  --no-cache ffmpeg

COPY . /code/