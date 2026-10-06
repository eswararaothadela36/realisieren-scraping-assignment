import logging
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================
# CONFIGURATION
# ==========================================

BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = "output/books.csv"
LOG_FILE = "logs/scraper.log"


# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# CREATE REQUEST SESSION
# ==========================================

def create_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# ==========================================
# CONVERT RATING
# ==========================================

def get_rating(rating_classes):

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for rating_name, rating_value in rating_map.items():

        if rating_name in rating_classes:
            return rating_value

    return None


# ==========================================
# SCRAPE BOOK DETAIL PAGE
# ==========================================

def scrape_book_details(session, book_url):

    try:

        response = session.get(
            book_url,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # ------------------------------
        # Category
        # ------------------------------

        breadcrumbs = soup.select(
            "ul.breadcrumb li a"
        )

        category = None

        if len(breadcrumbs) >= 3:

            category = breadcrumbs[2].get_text(
                strip=True
            )

        # ------------------------------
        # Description
        # ------------------------------

        description = None

        description_element = soup.select_one(
            "#product_description + p"
        )

        if description_element:

            description = description_element.get_text(
                " ",
                strip=True
            )

        # ------------------------------
        # Availability
        # ------------------------------

        availability = None

        availability_element = soup.select_one(
            "p.instock.availability"
        )

        if availability_element:

            availability = availability_element.get_text(
                " ",
                strip=True
            )

        return (
            category,
            description,
            availability
        )

    except requests.RequestException as error:

        logging.error(
            f"Detail page request failed: {book_url} - {error}"
        )

        return (
            None,
            None,
            None
        )

    except Exception as error:

        logging.exception(
            f"Unexpected detail page error: {book_url} - {error}"
        )

        return (
            None,
            None,
            None
        )


# ==========================================
# SCRAPE ALL BOOKS
# ==========================================

def scrape_books():

    session = create_session()

    books = []

    page_url = BASE_URL

    page_number = 1

    while page_url:

        print()
        print(
            f"Scraping page {page_number}: {page_url}"
        )

        logging.info(
            f"Scraping page {page_number}: {page_url}"
        )

        try:

            # ------------------------------
            # Request Page
            # ------------------------------

            response = session.get(
                page_url,
                timeout=10
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # ------------------------------
            # Find Books
            # ------------------------------

            book_items = soup.select(
                "article.product_pod"
            )

            print(
                f"Found {len(book_items)} books on page {page_number}"
            )

            # ------------------------------
            # Process Each Book
            # ------------------------------

            for item in book_items:

                # Title
                title_element = item.select_one(
                    "h3 a"
                )

                # Price
                price_element = item.select_one(
                    ".price_color"
                )

                # Rating
                rating_element = item.select_one(
                    ".star-rating"
                )

                # Availability
                availability_element = item.select_one(
                    ".availability"
                )

                # Skip if title missing
                if not title_element:

                    continue

                # ==================================
                # TITLE
                # ==================================

                title = title_element.get(
                    "title",
                    ""
                ).strip()

                # ==================================
                # PRICE
                # ==================================

                price_text = ""

                if price_element:

                    price_text = price_element.get_text(
                        strip=True
                    )

                price = None

                if price_text:

                    # Fix encoding issue:
                    # Â51.77 → 51.77

                    clean_price = (
                        price_text
                        .replace("£", "")
                        .replace("Â", "")
                        .strip()
                    )

                    try:

                        price = float(
                            clean_price
                        )

                    except ValueError:

                        price = None

                        logging.warning(
                            f"Invalid price: {price_text}"
                        )

                # ==================================
                # RATING
                # ==================================

                rating = None

                if rating_element:

                    rating = get_rating(
                        rating_element.get(
                            "class",
                            []
                        )
                    )

                # ==================================
                # AVAILABILITY
                # ==================================

                availability = None

                if availability_element:

                    availability = availability_element.get_text(
                        " ",
                        strip=True
                    )

                # ==================================
                # BOOK URL
                # ==================================

                relative_url = title_element.get(
                    "href",
                    ""
                )

                book_url = urljoin(
                    page_url,
                    relative_url
                )

                # ==================================
                # DETAIL PAGE
                # ==================================

                (
                    category,
                    description,
                    detail_availability
                ) = scrape_book_details(
                    session,
                    book_url
                )

                # Prefer detail page availability
                if detail_availability:

                    availability = detail_availability

                # ==================================
                # CREATE BOOK RECORD
                # ==================================

                book_data = {

                    "source": "Books to Scrape",

                    "source_url": book_url,

                    "name_or_title": title,

                    "category": category,

                    "price": price,

                    "rating": rating,

                    "author": None,

                    "tags": None,

                    "description": description,

                    "availability": availability
                }

                books.append(
                    book_data
                )

                print(
                    f"  Scraped: {title}"
                )

                logging.info(
                    f"Scraped book: {title}"
                )

                # Small delay
                time.sleep(0.1)

            # ==================================
            # PAGINATION
            # ==================================

            next_button = soup.select_one(
                "li.next a"
            )

            if next_button:

                next_url = next_button.get(
                    "href"
                )

                page_url = urljoin(
                    page_url,
                    next_url
                )

                page_number += 1

            else:

                page_url = None

        except requests.RequestException as error:

            logging.error(
                f"Page request failed: {page_url} - {error}"
            )

            print(
                f"Request failed: {error}"
            )

            break

        except Exception as error:

            logging.exception(
                f"Unexpected error on page {page_url}: {error}"
            )

            print(
                f"Unexpected error: {error}"
            )

            break

    return books


# ==========================================
# SAVE DATA
# ==========================================

def save_books(books):

    if not books:

        print(
            "No books were scraped."
        )

        return

    dataframe = pd.DataFrame(
        books
    )

    # ==================================
    # REMOVE DUPLICATES
    # ==================================

    dataframe = dataframe.drop_duplicates(
        subset=["source_url"]
    )

    # ==================================
    # SAVE CSV
    # ==================================

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print()
    print(
        f"CSV saved successfully: {OUTPUT_FILE}"
    )

    print(
        f"Final records: {len(dataframe)}"
    )

    # ==================================
    # DISPLAY SAMPLE
    # ==================================

    print()
    print("First 5 records:")

    print(
        dataframe.head()
    )


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    print(
        "====================================="
    )

    print(
        "   BOOKS TO SCRAPE - WEB SCRAPER"
    )

    print(
        "====================================="
    )

    print()

    logging.info(
        "Books scraper started"
    )

    books = scrape_books()

    print()
    print(
        "====================================="
    )

    print(
        "Scraping completed!"
    )

    print(
        f"Total books scraped: {len(books)}"
    )

    print(
        "====================================="
    )

    save_books(
        books
    )

    logging.info(
        f"Books scraper completed. Total records: {len(books)}"
    )