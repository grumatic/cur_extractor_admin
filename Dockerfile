FROM python:3.9.10
# Fails to install pandas on 3.9.10-alpine

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src /app
COPY ./static /static
COPY ./scripts /scripts

WORKDIR /app