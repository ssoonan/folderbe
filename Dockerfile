FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY ./ ./
EXPOSE 8000

RUN chmod 555 boot.sh

CMD ["./boot.sh"]