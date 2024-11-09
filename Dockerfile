FROM python:3.12-slim

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["gunicorn",  "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:create_app()"]
