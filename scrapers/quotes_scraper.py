import logging
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://quotes.toscrape.com/"
OUTPUT_FILE = "output/quotes.csv"
LOG_FILE = "logs/scraper.log"


# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------------
# Create Session with Retries
# -----------------------------

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


# -----------------------------
# Scrape Quotes
# -----------------------------

def scrape_quotes():

    session = create_session()

    quotes = []

    page_url = BASE_URL

    page_number = 1

    while page_url:

        print(
            f"\nScraping page {page_number}: {page_url}"
        )

        logging.info(
            f"Scraping quotes page {page_number}: {page_url}"
        )

        try:

            response = session.get(
                page_url,
                timeout=10
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            quote_items = soup.select(
                "div.quote"
            )

            print(
                f"Found {len(quote_items)} quotes"
            )

            for item in quote_items:

                # -----------------------------
                # Quote Text
                # -----------------------------

                quote_element = item.select_one(
                    "span.text"
                )

                quote_text = ""

                if quote_element:

                    quote_text = quote_element.get_text(
                        " ",
                        strip=True
                    )

                # -----------------------------
                # Author
                # -----------------------------

                author_element = item.select_one(
                    "small.author"
                )

                author = ""

                if author_element:

                    author = author_element.get_text(
                        strip=True
                    )

                # -----------------------------
                # Author URL
                # -----------------------------

                author_link = item.select_one(
                    "span a"
                )

                author_url = None

                if author_link:

                    author_url = urljoin(
                        page_url,
                        author_link.get("href", "")
                    )

                # -----------------------------
                # Tags
                # -----------------------------

                tag_elements = item.select(
                    "div.tags a.tag"
                )

                tags = []

                for tag in tag_elements:

                    tags.append(
                        tag.get_text(
                            strip=True
                        )
                    )

                tags_text = ", ".join(tags)

                # -----------------------------
                # Create Record
                # -----------------------------

                quote_data = {

                    "source": "Quotes to Scrape",

                    "source_url": page_url,

                    "name_or_title": quote_text,

                    "category": None,

                    "price": None,

                    "rating": None,

                    "author": author,

                    "tags": tags_text,

                    "description": quote_text,

                    "author_url": author_url
                }

                quotes.append(
                    quote_data
                )

                print(
                    f"  Scraped: {quote_text[:60]}"
                )

                logging.info(
                    f"Scraped quote by {author}"
                )

                time.sleep(0.1)

            # -----------------------------
            # Pagination
            # -----------------------------

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
                f"Request failed: {page_url} - {error}"
            )

            print(
                f"Request failed: {error}"
            )

            break

        except Exception as error:

            logging.exception(
                f"Unexpected error: {error}"
            )

            print(
                f"Unexpected error: {error}"
            )

            break

    return quotes


# -----------------------------
# Save Quotes
# -----------------------------

def save_quotes(quotes):

    if not quotes:

        print(
            "\nNo quotes were scraped."
        )

        return

    dataframe = pd.DataFrame(
        quotes
    )

    # Remove duplicate quotes
    dataframe = dataframe.drop_duplicates(
        subset=[
            "name_or_title",
            "author"
        ]
    )

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

    print()
    print("First 5 records:")

    print(
        dataframe.head()
    )


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    print(
        "====================================="
    )

    print(
        "    QUOTES TO SCRAPE - SCRAPER"
    )

    print(
        "====================================="
    )

    logging.info(
        "Quotes scraper started"
    )

    quotes = scrape_quotes()

    print()
    print(
        "====================================="
    )

    print(
        "Scraping completed!"
    )

    print(
        f"Total quotes scraped: {len(quotes)}"
    )

    print(
        "====================================="
    )

    save_quotes(
        quotes
    )

    logging.info(
        f"Quotes scraper completed. Total records: {len(quotes)}"
    )