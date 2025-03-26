import os
import psycopg2
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Retrieve database connection details from environment variables
database_name = os.getenv("DATABASE_NAME")
database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASSWORD")
database_host = os.getenv("DATABASE_HOST")
database_port = os.getenv("DATABASE_PORT")

# Check if all database connection details are set
if not all([database_name, database_user, database_password, database_host, database_port]):
    logging.error("One or more database connection environment variables are not set.")
    exit(1)

# Function to create the 'files' table if it doesn't exist
def create_table():
    try:
        logging.info("Connecting to the database to create the 'files' table...")
        conn = psycopg2.connect(
            dbname=database_name,
            user=database_user,
            password=database_password,
            host=database_host,
            port=database_port
        )
        cursor = conn.cursor()

        # SQL query to create the 'files' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100)
            )
        ''')
        conn.commit()
        logging.info("'files' table created successfully.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed.")

def insert_data(cursor, title):
    try:
        cursor.execute('''
            INSERT INTO files (title)
            VALUES (%s)
        ''', (title,))
        logging.info("file inserted successfully.")
    except Exception as e:
        logging.error(f"Error inserting file: {e}")

class WebDriver:
    def __init__(self):
        pass

    def run_scraping(self, cursor, title):
        logging.info(f"Fetching data from: {title}")
        response = requests.get(title)
        if response.status_code == 200:
            logging.info("Data fetched successfully.")
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the title from the specified selector
            title = soup.select_one('.gs_r.gs_or.gs_scl > .gs_ri > .gs_rt').text.strip() if soup.select_one('.gs_r.gs_or.gs_scl > .gs_ri > .gs_rt') else ""

            # Insert scraped data into the database
            insert_data(cursor, title)
            logging.info("Scraped data inserted into the database.")
        else:
            logging.error(f"Failed to fetch data: {response.status_code}")

web_driver = WebDriver()

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        logging.warning("Invalid input. 'query' is required.")
        return jsonify({"error": "Invalid input. 'query' is required."}), 400

    search_query = data['query']
    logging.info(f"Received search query: {search_query}")
    
    search_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={search_query}"

    try:
        logging.info("Connecting to the database to insert file...")
        conn = psycopg2.connect(
            dbname=database_name,
            user=database_user,
            password=database_password,
            host=database_host,
            port=database_port
        )
        cursor = conn.cursor()
        
        # Run the scraping
        web_driver.run_scraping(cursor, search_url)
        conn.commit()
    except Exception as e:
        logging.error(f"Error inserting file: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed.")

    # Return a success response
    return jsonify({"message": "Scraping started successfully!"})

create_table()
