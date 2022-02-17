FROM python:3.9.10
# Fails to install pandas on 3.9.10-alpine

ENV PATH="/scripts:${PATH}"

RUN pip install --upgrade pip

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
COPY ./src /app
WORKDIR /app

COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

CMD ["/scripts/entrypoint.sh"]