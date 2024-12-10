FROM python:3.9-slim

WORKDIR /app

COPY producer.py ./producer

RUN pip install pika flask psycopg2-binary 

CMD ["python", "producer.py"]

