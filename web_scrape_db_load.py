from playwright.sync_api import sync_playwright
import psycopg2
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(database_url, sslmode='require')

def update_database(conn, item_name, price, currency_code, existing_items):
    cursor = conn.cursor()
    now = datetime.now()

    try:
        cursor.execute("SELECT ID, ItemName, Price, CurrencyCode, LastUpdated FROM Items WHERE ItemName = %s ORDER BY LastUpdated ASC", (item_name,))
        records = cursor.fetchall()

        existing_items.add((item_name, price))

        print(f"Found {len(records)} records for item name {item_name}.")  # Debugging output

        if not records:
            cursor.execute("INSERT INTO Items (ItemName, Price, CurrencyCode, LastUpdated) VALUES (%s, %s, %s, %s)",
                           (item_name, price, currency_code, now))
            conn.commit()
            print(f"Inserted new record for {item_name}.")
        else:
            current_prices = {record[2] for record in records}
            if price not in current_prices:
                cursor.execute("INSERT INTO Items (ItemName, Price, CurrencyCode, LastUpdated) VALUES (%s, %s, %s, %s)",
                               (item_name, price, currency_code, now))
                conn.commit()
                print(f"Inserted new record for {item_name} with a new price {price}.")
            else:
                print("No update needed for existing record as price is unchanged.")

    except Exception as e:
        conn.rollback()
        print(f"Failed to update database: {e}")
    finally:
        cursor.close()

def archive_nonexistent_items(conn, existing_items):
    cursor = conn.cursor()
    now = datetime.now()

    try:
        cursor.execute("SELECT ID, ItemName, Price, CurrencyCode, LastUpdated FROM Items")
        records = cursor.fetchall()

        for record in records:
            if (record[1], record[2]) not in existing_items:
                cursor.execute("INSERT INTO Archive (ItemName, Price, CurrencyCode, LastUpdated) VALUES (%s, %s, %s, %s)",
                               (record[1], record[2], record[3], record[4]))
                cursor.execute("DELETE FROM Items WHERE ID = %s", (record[0],))
                print(f"Archived record for {record[1]} with price {record[2]} as it no longer exists in the current scrape.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Failed to archive non-existent items: {e}")
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
    existing_items = set()

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
            price = float(integer + decimal)
            update_database(conn, item_name, price, currency_code, existing_items)

        # Archive items that no longer exist
        archive_nonexistent_items(conn, existing_items)

    except Exception as e:
        print("An error occurred while processing items:", e)

    close_db(conn)
