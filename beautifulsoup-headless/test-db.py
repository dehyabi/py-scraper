import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# Load environment variables from .env file
load_dotenv()

def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT")
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")

    return connection

# Test the connection
connection = create_connection()