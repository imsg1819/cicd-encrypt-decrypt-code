
from flask import Flask, request, jsonify
import uuid
import psycopg2
import pika
import json
import base64

app = Flask(__name__)

# Database configuration
DB_HOST = 'postgres'
DB_NAME = 'my_database'  # Update this if necessary
DB_USER = 'postgres'      # Change this to your desired username
DB_PASS = 'mysecretpassword'  # Change this to your desired password

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def create_tables():
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            # Create encode table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS encode (
                    id VARCHAR(32) PRIMARY KEY,
                    plain_text TEXT NOT NULL
                );
            """)

            # Create get_encrypted_text table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS get_encrypted_text (
                    id VARCHAR(32) PRIMARY KEY,
                    encrypted_text TEXT NOT NULL
                );
            """)

            # Create decode table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS decode (
                    id VARCHAR(32) PRIMARY KEY,
                    encrypted_text TEXT NOT NULL
                );
            """)

            # Create get_decrypted_text table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS get_decrypted_text (
                    id VARCHAR(32) PRIMARY KEY,
                    plain_text TEXT NOT NULL
                );
            """)

    conn.close()

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/encode', methods=['POST'])
def encode_plain_text():
    data = request.json
    plain_text = data.get('plain_text')

    if plain_text is None:
        return jsonify({"error": "Please provide 'plain_text' in the JSON body."}), 400

    unique_id = uuid.uuid4().hex  # Generate a unique ID

    # Encode the plain text
    encrypted_text = base64.b64encode(plain_text.encode()).decode()

    # Store the plain text in the database
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO encode (id, plain_text) VALUES (%s, %s)", (unique_id, plain_text))

            # Store the encrypted text
            cur.execute("INSERT INTO get_encrypted_text (id, encrypted_text) VALUES (%s, %s)", (unique_id, encrypted_text))

    message = {
        'action': 'encode',
        'text': encrypted_text,
        'id': unique_id
    }

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='encoding_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='encoding_queue', body=json.dumps(message))
    connection.close()

    return jsonify({"message": "Encoding request sent successfully!", "unique_id": unique_id})

@app.route('/get_encrypted', methods=['POST'])
def get_encrypted():
    data = request.json
    unique_id = data.get('id')

    if unique_id is None:
        return jsonify({"error": "Please provide 'id' in the JSON body."}), 400

    # Retrieve the encrypted text based on the ID
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT encrypted_text FROM get_encrypted_text WHERE id = %s", (unique_id,))
            result = cur.fetchone()

            if result:
                encrypted_text = result[0]
                return jsonify({"unique_id": unique_id, "encrypted_text": encrypted_text})
            else:
                return jsonify({"error": "Invalid ID or not found."}), 404

@app.route('/decode', methods=['POST'])
def decode_text():
    data = request.json
    encrypted_text = data.get('encrypted_text')

    if encrypted_text is None:
        return jsonify({"error": "Please provide 'encrypted_text' in the JSON body."}), 400

    unique_id = uuid.uuid4().hex  # Generate a unique ID for the decoded entry

    # Decode the encrypted text to get the plain text
    plain_text = base64.b64decode(encrypted_text).decode()

    # Store the encrypted text in the database
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO decode (id, encrypted_text) VALUES (%s, %s)", (unique_id, encrypted_text))
            cur.execute("INSERT INTO get_decrypted_text (id, plain_text) VALUES (%s, %s)", (unique_id, plain_text))

    message = {
        'action': 'decode',
        'text': encrypted_text,
        'id': unique_id
    }

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='decoding_queue', durable=True)
    channel.basic_publish(exchange='', routing_key='decoding_queue', body=json.dumps(message))
    connection.close()

    return jsonify({"message": "Decoding request sent successfully!", "unique_id": unique_id})

@app.route('/get_decrypted', methods=['POST'])
def get_decrypted():
    data = request.json
    unique_id = data.get('id')

    if unique_id is None:
        return jsonify({"error": "Please provide 'id' in the JSON body."}), 400

    # Retrieve the decoded text based on the ID
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT plain_text FROM get_decrypted_text WHERE id = %s", (unique_id,))
            result = cur.fetchone()

            if result:
                decoded_text = result[0]
                return jsonify({"unique_id": unique_id, "decoded_text": decoded_text})
            else:
                return jsonify({"error": "Invalid ID or not found."}), 404

if __name__ == '__main__':
    create_tables()  # Create tables if they don't exist
    app.run(debug=True, host="0.0.0.0", port=4321)

