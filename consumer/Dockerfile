FROM python:3.9-slim

WORKDIR /app

COPY consumer.py ./consumer

RUN pip install pika psycopg2-binary flask  

CMD ["python", "consumer.py"]

