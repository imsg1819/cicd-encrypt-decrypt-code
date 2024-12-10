'''
import pika
import psycopg2
import base64
import json

DB_HOST = 'postgres'
DB_NAME = 'my_database'
DB_USER = 'postgres'
DB_PASS = 'mysecretpassword'

# Establish a database connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def on_message_received(ch, method, properties, body):
    message = json.loads(body)
    
    if message['action'] == 'encode':
        plain_text = message['text']
        unique_id = message['id']
        
        # Encode the plain text to base64
        encrypted_text = base64.b64encode(plain_text.encode()).decode()
        
        # Store the encoded text and plain text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO encrypted_texts (id, encrypted_text, plain_text) VALUES (%s, %s, %s)",
                    (unique_id, encrypted_text, plain_text)
                )
        print(f"Encoded and stored: {unique_id}")
    
    elif message['action'] == 'decode':
        encrypted_text = message['text']
        unique_id = message['id']
        
        # Decode the base64 text to get the original plain text
        try:
            plain_text = base64.b64decode(encrypted_text).decode()
        except Exception as e:
            print("Invalid base64 text:", e)
            return
        
        # Store the decoded text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO decoded_texts (id, decoded_text) VALUES (%s, %s)",
                    (unique_id, plain_text)
                )
        print(f"Decoded and stored: {unique_id}")

def main():
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq', 5672, '/', pika.PlainCredentials('guest', 'guest'))
        )
        channel = connection.channel()

        # Declare the queues (make sure they exist)
        channel.queue_declare(queue='encoding_queue', durable=True)
        channel.queue_declare(queue='decoding_queue', durable=True)

        # Start consuming from both queues
        channel.basic_consume(queue='encoding_queue', on_message_callback=on_message_received, auto_ack=True)
        channel.basic_consume(queue='decoding_queue', on_message_callback=on_message_received, auto_ack=True)

        print("Waiting for messages...")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Failed to connect to RabbitMQ:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    main()

'''




'''

import pika
import psycopg2
import base64
import json

DB_HOST = 'postgres'
DB_NAME = 'my_database'
DB_USER = 'postgres'
DB_PASS = 'mysecretpassword'

# Establish a database connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def on_message_received(ch, method, properties, body):
    message = json.loads(body)

    if message['action'] == 'encode':
        plain_text = message['text']
        unique_id = message['id']

        # Encode the plain text to base64
        encrypted_text = base64.b64encode(plain_text.encode()).decode()

        # Store the encoded text and plain text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO encode (plain_text) VALUES (%s) RETURNING id",
                    (plain_text,)
                )
                encode_id = cur.fetchone()[0]  # Get the new ID

                cur.execute(
                    "INSERT INTO get_encrypted_text (id, encrypted_text) VALUES (%s, %s)",
                    (encode_id, encrypted_text)
                )

        print(f"Encoded and stored: {unique_id}")

    elif message['action'] == 'decode':
        encrypted_text = message['text']
        unique_id = message['id']

        # Decode the base64 text to get the original plain text
        try:
            plain_text = base64.b64decode(encrypted_text).decode()
        except Exception as e:
            print("Invalid base64 text:", e)
            return

        # Store the decoded text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO decode (encrypted_text) VALUES (%s) RETURNING id",
                    (encrypted_text,)
                )
                decode_id = cur.fetchone()[0]  # Get the new ID

                cur.execute(
                    "INSERT INTO get_decrypted_text (id, plain_text) VALUES (%s, %s)",
                    (decode_id, plain_text)
                )

        print(f"Decoded and stored: {unique_id}")

def main():
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq', 5672, '/', pika.PlainCredentials('guest', 'guest'))
        )
        channel = connection.channel()

        # Declare the queues (make sure they exist)
        channel.queue_declare(queue='encoding_queue', durable=True)
        channel.queue_declare(queue='decoding_queue', durable=True)

        # Start consuming from both queues
        channel.basic_consume(queue='encoding_queue', on_message_callback=on_message_received, auto_ack=True)
        channel.basic_consume(queue='decoding_queue', on_message_callback=on_message_received, auto_ack=True)

        print("Waiting for messages...")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Failed to connect to RabbitMQ:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    main()

'''


import pika
import psycopg2
import base64
import json
import uuid

DB_HOST = 'postgres'
DB_NAME = 'my_database'
DB_USER = 'postgres'
DB_PASS = 'mysecretpassword'

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def on_message_received(ch, method, properties, body):
    message = json.loads(body)

    if message['action'] == 'encode':
        plain_text = message['text']
        unique_id = message['id']

        # Store the plain text and encrypted text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Store the plain text (if needed) and the encrypted text
                cur.execute("INSERT INTO get_encrypted_text (id, encrypted_text) VALUES (%s, %s)",
                            (unique_id, plain_text))  # Adjust as necessary

        print(f"Encoded and stored: {unique_id}")

    elif message['action'] == 'decode':
        encrypted_text = message['text']
        unique_id = message['id']

        # Decode the base64 text to get the original plain text
        try:
            plain_text = base64.b64decode(encrypted_text).decode()
        except Exception as e:
            print("Invalid base64 text:", e)
            return

        # Store the decoded text in the database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO get_decrypted_text (id, plain_text) VALUES (%s, %s)",
                            (unique_id, plain_text))  # Use the new string ID

        print(f"Decoded and stored: {unique_id}")

def main():
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('rabbitmq', 5672, '/', pika.PlainCredentials('guest', 'guest'))
        )
        channel = connection.channel()

        # Declare the queues (make sure they exist)
        channel.queue_declare(queue='encoding_queue', durable=True)
        channel.queue_declare(queue='decoding_queue', durable=True)

        # Start consuming from both queues
        channel.basic_consume(queue='encoding_queue', on_message_callback=on_message_received, auto_ack=True)
        channel.basic_consume(queue='decoding_queue', on_message_callback=on_message_received, auto_ack=True)

        print("Waiting for messages...")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Failed to connect to RabbitMQ:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    main()

