import sqlite3
from datetime import datetime
import os
import asyncio
import pprint
import html
import logging
import pytz
import re
import streamlit as st
from openai import OpenAI
from aiconfig import AIConfigRuntime, CallbackManager, CallbackEvent, InferenceOptions
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    database_url = os.environ['DATABASE_URL']
    return psycopg2.connect(database_url, sslmode='require')

#api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_est_time():
    utc_time = datetime.utcnow()
    est = pytz.timezone('America/New_York')
    return utc_time.replace(tzinfo=pytz.utc).astimezone(est)

def format_last_updated(timestamp):
    try:
        # Convert timestamp to datetime object if it's a string
        if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        # Convert UTC time to EST
        est = pytz.timezone('America/New_York')
        formatted_date = timestamp.astimezone(est).strftime("%Y-%m-%d %H:%M") + " EST"
    except Exception as e:
        print("Error formatting date:", e)
        formatted_date = "Unknown Timestamp Format"
    return formatted_date


def get_item_names():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT ItemName FROM Items ORDER BY ItemName ASC")
            item_names = [row[0] for row in cursor.fetchall()]
    return item_names


def generate_items_regex():
    item_names = get_item_names()
    escaped_item_names = [re.escape(name) for name in item_names]
    return '|'.join(escaped_item_names)

def retrieve_data(item_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if item_name:
        logging.info(f"Retrieving data for item: {item_name}")
        query = "SELECT ItemName, Price, CurrencyCode, LastUpdated FROM Items WHERE ItemName = %s"
        cursor.execute(query, (item_name,))
    else:
        query = "SELECT ItemName, Price, CurrencyCode, LastUpdated FROM Items ORDER BY Price DESC"
        cursor.execute(query)
    rows = cursor.fetchall()
    logging.info(f"Query executed: {query} | Rows fetched: {len(rows)}")
    conn.close()
    return rows

def log_response(llm_response, item_name, actual_price, llm_name, llm_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    est_time = get_est_time()
    cursor.execute('''
        INSERT INTO LLMQueryLog (LLMResponse, ItemName, Price, LLMName, LLMPrice, QueriedOn)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (llm_response, item_name, actual_price, llm_name, llm_price, est_time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def extract_name_and_price(llm_response):
    items_regex_pattern = generate_items_regex()
    # Regex to specifically capture monetary values followed by "USD"
    price_pattern = re.compile(r"(\d+\.?\d*)\s*USD")
    # Modify the name pattern to allow matching across typical non-word boundaries like hyphens
    name_pattern = re.compile(rf"({items_regex_pattern})", re.IGNORECASE)
    
    price_match = price_pattern.search(llm_response)
    llm_price = price_match.group(1) if price_match else "Unknown"  # Extract the matched price group

    # Search for the longest matching name, since some names are substrings of others
    name_matches = name_pattern.findall(llm_response)
    llm_name = max(name_matches, key=len) if name_matches else "Unknown"

    return llm_name, llm_price


def sanitize_text(text):
    return html.unescape(text)

def serialize_retrieved_data(data):
    out = {sanitize_text(row[0]): {"Price": row[1], "CurrencyCode": row[2], "LastUpdated": format_last_updated(row[3])} for row in data}
    return out

async def generate(query, context, prompt):
    config = AIConfigRuntime.load("sc-shop-assist.aiconfig.json")
    params = {
        "query": query,
        "context": context,
    }
    inference_options = InferenceOptions(stream=True)
    output = await config.run_and_get_output_text(prompt, params=params, run_with_dependencies=True, options=inference_options)
    return output

async def run_query(item_query, prompt="generate"):
    data = retrieve_data(item_query)
    context = serialize_retrieved_data(data)
    output = await generate(item_query, context, prompt)
    return output, data  # Return both output and data

async def process_user_query(user_query):
    response_text, item_data = await run_query(user_query)
    if item_data:  # Ensure there is data to process
        llm_name, llm_price = extract_name_and_price(response_text)
        # Log only if the item name matches the user query exactly
        log_response(response_text, user_query, item_data[0][1], llm_name, llm_price)
    return response_text

async def main():
    user_query = "example item query"
    result = await process_user_query(user_query)
    print("Query result:", result)

if __name__ == "__main__":
    asyncio.run(main())

