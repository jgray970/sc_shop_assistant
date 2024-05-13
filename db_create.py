#import sqlite3
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')

def initialize_db():
    # Ensure these are filled with your actual database credentials
    conn = psycopg2.connect(database_url, sslmode='require')
    cursor = conn.cursor()
    
    # Create Items table if it does not exist with PostgreSQL compatible syntax
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            ID SERIAL PRIMARY KEY,
            ItemName TEXT,
            Price REAL,
            CurrencyCode TEXT,
            LastUpdated TIMESTAMP
        )
    ''')
    
    # Create Archive table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Archive (
            ID SERIAL PRIMARY KEY,
            ItemName TEXT,
            Price REAL,
            CurrencyCode TEXT,
            LastUpdated TIMESTAMP
        )
    ''')
    
    # Drop and recreate LLMQueryLog table to ensure clean setup
    cursor.execute('''
    CREATE TABLE LLMQueryLog (
        ID SERIAL PRIMARY KEY,
        LLMResponse TEXT,
        LLMName TEXT,
        LLMPrice TEXT,
        ItemName TEXT,
        Price TEXT,
        QueriedOn TIMESTAMP
    )
    ''')
    
    conn.commit()
    return conn

def close_db(conn):
    conn.close()

# Main execution block
if __name__ == "__main__":
    # Initialize the database
    conn = initialize_db()
    print("Database initialized.")
    
    # Close the database connection
    close_db(conn)
    print("Database connection closed.")
