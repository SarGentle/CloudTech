FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
RUN apt-get update -y

ENV PYTHONUNBUFFERED 1

RUN apt-get update
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt