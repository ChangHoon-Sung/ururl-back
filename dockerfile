FROM python:3.10.2

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "ururl.wsgi", "-k", "gevent", "--workers", "5", "--log-file", "-", "--log-level", "debug"]
