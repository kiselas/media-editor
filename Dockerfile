FROM python:3.10.8-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN DEBIAN_FRONTEND=noninteractive apt -y update
RUN apt -y upgrade
RUN apt -y install gifsicle ffmpeg
RUN apt clean
RUN pip install -r requirements.txt

COPY . /code/