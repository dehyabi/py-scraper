# Py-Scraper

This project is a web scraper built using Flask, BeautifulSoup, and PostgreSQL. It allows users to search for information and store the results in a PostgreSQL database.

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/dehyabi/py-scraper.git
   cd py-scraper
   ```

2. **Choose your scraping tools:**

   - **beautifulsoup-headless**: Uses BeautifulSoup for scraping without opening a browser.
   - **scrapegraphai-headless**: Uses ScrapeGraphAI for scraping without opening a browser (need OpenAI API Key).
   - **selenium-headless**: Uses Selenium to scrape without opening a browser.
   - **selenium-gui**: Uses Selenium with a graphical user interface (need Chrome installed).

   For example you use beautifulsoup-headless just do:

   ```bash
   cd beautifulsoup-headless
   ```

3. **Setup the environment:**

   - Create a `.env` file in the root directory and add your database connection details.
   - Example:
     ```
     DATABASE_NAME=your_database_name
     DATABASE_USER=your_database_user
     DATABASE_PASSWORD=your_database_password
     DATABASE_HOST=localhost
     DATABASE_PORT=5432
     ```

4. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

6. **Test the database connection:**

   ```bash
   python3 test-db.py
   ```

7. **Run the application:**

   ```bash
   flask run
   ```

8. **Test the search endpoint:**
   Use curl to test the search functionality:
   ```bash
   curl -X POST http://127.0.0.1:5000/search -H "Content-Type: application/json" -d '{"query": "technology"}'
   ```

## Database Interaction

- To connect to PostgreSQL, use the following command:

  ```bash
  sudo postgres psql -d your_database_name
  ```

- You can view the inserted data with:

  ```sql
  SELECT * FROM table_name;
  ```

  Example of inserted data:

  ```
  -[ RECORD 1 ]-------------------------------------------------
  id    | 1
  title | Ultracapacitors: why, how, and where is the technology
  ```

  **Note:** The database setup and commands may vary depending on your database system.

## Success Logs

Check the logs for information on the operations performed by the application.

```
 * Running on http://127.0.0.1:5000
2025-03-27 05:49:20,478 - INFO - Press CTRL+C to quit
2025-03-27 05:49:50,642 - INFO - Received search query: technology
2025-03-27 05:49:50,642 - INFO - Connecting to the database to insert file...
2025-03-27 05:49:50,679 - INFO - Fetching data from: https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=technology
2025-03-27 05:49:52,352 - INFO - Data fetched successfully.
2025-03-27 05:49:52,484 - INFO - file inserted successfully.
2025-03-27 05:49:52,484 - INFO - Scraped data inserted into the database.
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
