from playwright.sync_api import sync_playwright
import sqlite3
from datetime import datetime
import time
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(database_url, sslmode='require')


def update_database(conn, item_name, price, currency_code):
    cursor = conn.cursor()
    now = datetime.now()

    try:
        # Fetch existing records for the given item name using PostgreSQL's placeholder %s
        cursor.execute("SELECT ID, Price, CurrencyCode, LastUpdated FROM Items WHERE ItemName = %s ORDER BY LastUpdated ASC", (item_name,))
        records = cursor.fetchall()

        print(f"Found {len(records)} records for item name {item_name}.")  # Debugging output

        if not records:
            # No records exist, insert new one using PostgreSQL's placeholder %s
            cursor.execute("INSERT INTO Items (ItemName, Price, CurrencyCode, LastUpdated) VALUES (%s, %s, %s, %s)",
                           (item_name, price, currency_code, now))
            conn.commit()
            print(f"Inserted new record for {item_name}.")

        elif len(records) == 1:
            # One record exists, check the price
            if records[0][1] != price:
                # Price is different, insert new record using PostgreSQL's placeholder %s
                cursor.execute("INSERT INTO Items (ItemName, Price, CurrencyCode, LastUpdated) VALUES (%s, %s, %s, %s)",
                               (item_name, price, currency_code, now))
                conn.commit()
                print(f"Inserted new record for {item_name} due to price change.")
            else:
                # Price is the same, do not update the timestamp
                print("No update needed for existing record as price is unchanged.")

        else:
            # Handle multiple records if necessary (your original code managed up to 2)
            print("Handling multiple records is not implemented in this snippet.")

    except Exception as e:
        conn.rollback()
        print(f"Failed to update database: {e}")
    finally:
        cursor.close()

def scroll_slowly(page):
    try:
        scroll_increment = 500
        delay_between_scrolls = 0.5
        max_attempts = 175
        attempts = 0
        last_scroll_position = None  # Variable to store the last scroll position

        while attempts < max_attempts:
            current_scroll = page.evaluate("window.scrollY")
            page_height = page.evaluate("document.documentElement.scrollHeight")
            print(f"Attempt {attempts + 1}: Current scroll position: {current_scroll}, Page height: {page_height}")

            # Check if current scroll position is the same as the last scroll position
            if current_scroll == last_scroll_position:
                print("No more scroll possible, end of page reached.")
                break
            if attempts == max_attempts:
                print("Max Attempts Reached")
            last_scroll_position = current_scroll  # Update last scroll position
            page.evaluate(f"window.scrollBy(0, {scroll_increment})")
            time.sleep(delay_between_scrolls)
            attempts += 1

        if attempts >= max_attempts:
            print("Max number of scroll attempts reached.")
    except Exception as e:
        print("An error occurred while scrolling:", e)

def close_db(conn):
    conn.close()

with sync_playwright() as p:
    conn = get_db_connection()
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    try:
        page.goto("https://robertsspaceindustries.com/store/pledge/browse/extras?sort=weight&direction=desc")
        page.is_visible('div.ItemWidget-image')
        page.wait_for_timeout(5000)
        selector = "span.BrowseFilterSort__group:has-text('Price')"
        element = page.wait_for_selector(selector)
        element.click()
        page.wait_for_timeout(1000)
        element.click()
        page.wait_for_timeout(2000)
        scroll_slowly(page)
    except Exception as e:
        print("An error occurred:", e)

    item_names = page.query_selector_all("h3.ItemWidget-main-title")
    price_elements = page.query_selector_all("span.TooltipTaxDescription.ItemWidgetPrices__taxes.FloatingTooltip__trigger")
    print("Items found:", len(item_names), "Prices found:", len(price_elements))

    try:
        for i in range(min(len(item_names), len(price_elements))):
            item_name = item_names[i].inner_text().strip()
            integer = price_elements[i].query_selector("span.Price-price-integer").inner_text().strip()
            decimal = price_elements[i].query_selector("span.Price-decimals").inner_text().strip()
            currency_code = price_elements[i].query_selector("span.Price-currency-code").inner_text().strip()
            price = integer + decimal
            update_database(conn, item_name, price, currency_code)

    except Exception as e:
        print("An error occurred while processing items:", e)

    close_db(conn)
