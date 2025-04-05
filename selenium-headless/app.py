import os
import psycopg2
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                file_type VARCHAR(100)
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

def insert_files(cursor, title, url, description=None, file_type=None):
    try:
        cursor.execute('''
            INSERT INTO files (title, url, description, file_type)
            VALUES (%s, %s, %s, %s)
        ''', (title, url, description, file_type))
        logging.info("File inserted successfully.")
    except Exception as e:
        logging.error(f"Error inserting file: {e}")

class WebDriver:
    def __init__(self):
        pass

    def run_scraping(self, cursor, search_url):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode (no GUI)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(search_url)
            # Extract title from the specified selector
            title_element = driver.find_element(By.CSS_SELECTOR, '.gs_r.gs_or.gs_scl > .gs_ri >.gs_rt')
            title = title_element.text.strip() if title_element else None

            # Extract URL from the specified selector
            url_element = driver.find_element(By.CSS_SELECTOR, '.gs_r.gs_or.gs_scl > .gs_ri > .gs_rt > a')
            url = url_element.get_attribute('href') if url_element else None

            # Extract description from the specified selector
            description_element = driver.find_element(By.CSS_SELECTOR, '.gs_r.gs_or.gs_scl > .gs_ri > .gs_rs')
            description = description_element.text.strip() if description_element else None

            # Extract file type from the specified selector
            file_type_element = driver.find_element(By.CSS_SELECTOR, '.gs_ctg2')
            file_type = file_type_element.text.strip().replace('[', '').replace(']', '') if file_type_element else None

            logging.info(f"Extracted title: {title}")
            logging.info(f"Extracted URL: {url}")
            logging.info(f"Extracted description: {description}")
            logging.info(f"Extracted file type: {file_type}")
        finally:
            driver.quit()  # Ensure the WebDriver is closed

        # Insert scraped data into the database
        if title or url or description or file_type:
            insert_files(cursor, title, url, description, file_type)
        logging.info("Scraped data inserted into the database.")

web_driver = WebDriver()

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        logging.warning("Invalid input. 'query' is required.")
        return jsonify({"error": "Invalid input. 'query' is required."}), 400

    search_query = data['query']
    logging.info(f"Received search query: {search_query}")
    
    search_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={search_query}&btnG="

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

        title = request.json.get('title')
        url = request.json.get('url')
        description = request.json.get('description')
        file_type = request.json.get('file_type')

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
