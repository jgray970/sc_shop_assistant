# Star Citizen (SC) Shop Assistant

The SC Shop Assistant serves as a way for players to get more conveniently get prices from the Roberts Space Industries website

## File Descriptions

### `backend.py`

This Python script serves as the backbone of a system integrating several external services like OpenAI, PostgreSQL, and Streamlit. It provides core functionalities such as establishing database connections, formatting dates, and executing queries. Additionally, it includes asynchronous functions to interact with a custom AI model using OpenAI's API, process and log responses based on user queries, and handle data serialization for client-facing interfaces. The code also showcases robust error handling and data sanitization to ensure the reliability and security of interactions.

### `sc-shop-assist.aiconfig.json`

The sc-shop-assist.aiconfig.json file configures an AI model specifically tailored for a Star Citizen shop assistant application, enabled by Last Mile AI. It outlines settings for interactions with a GPT-4 model, including a detailed system prompt that guides how the AI should respond to user queries about item prices. The prompt ensures the AI adheres to strict guidelines regarding data accuracy, user redirection, and formatting responses. Additionally, the configuration includes specific prompts that utilize context and query parameters to tailor the AI's user responses, focusing on maintaining predefined rules for data use and enhancing user assistance. 

### `frontend.py`

The frontend.py script leverages Streamlit to create a user-friendly interface for a Star Citizen price assistant tool. It offers two modes of interaction: searching or selecting from a list, enabling users to find and choose ships or items whose prices they want to retrieve. The application integrates with a backend system to process user queries asynchronously and display results. This setup includes features for dynamic suggestions during search, error handling for non-selections, and utilizes asynchronous programming to handle data processing efficiently.

### `db_create.py`

The db_create.py script is designed for setting up and managing the database structure necessary for an application using PostgreSQL (alternatively this could be created locally using SQLite, while adjusting SQL syntax). It initializes tables for storing item data, archival records, and logs of language model queries. The script uses environment variables for database credentials, ensuring secure access. Key functions include creating the Items, Archive, and LLMQueryLog tables with appropriate fields like ItemName, Price, CurrencyCode, and LastUpdated. The script ensures that these tables are created if they do not already exist. This setup facilitates organized data management and retrieval for application operations.

### `web_scrape_db_load.py`

The web_scrape_db_load.py script combines web scraping with database operations to update and maintain a dataset of item prices from the Roberts Space Industries website. It uses Playwright for web scraping in a Chromium browser, handling navigation, scrolling, and content extraction dynamically. The script includes robust database interaction through PostgreSQL (alternatively this could be created locally using SQLite, while adjusting SQL syntax), allowing it to check for existing records and update or insert new entries based on the fetched data. The functionality is designed to handle various potential scenarios, such as price changes or no records found, with detailed logging to assist in debugging and error handling.

### `scraping_data_.db`

A prefilled SQLite database file that can be used to test locally. Adjusting the backend and frontend files to point to local environment secrets will enable the ability to scrape data with web_scrape_db_load.py and land in a local db. For end-user testing and production focuses, a hosted db (heroku, aws, etc.) is suggested. All SQL syntax in relevant .py files should be adjusted to point to SQLite db instead of PostgeSQL db.
