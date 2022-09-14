FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY ./ ./
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000",  "-w", "5", "folderbe:app"]