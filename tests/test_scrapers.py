import os
import pandas as pd

from processing.data_processor import (
    clean_text,
    clean_price,
    clean_rating,
    remove_duplicates,
)


def test_clean_text():
    result = clean_text("   Hello    World   ")
    assert result == "Hello World"


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("Â£35.50") == 35.50


def test_clean_rating():
    assert clean_rating(4) == 4
    assert clean_rating("5") == 5
    assert clean_rating(6) is None


def test_remove_duplicate_books():
    data = pd.DataFrame([
        {
            "source": "Books to Scrape",
            "source_url": "book1",
            "name_or_title": "Book One",
            "category": "Fiction",
            "price": 10.0,
            "rating": 4,
            "author": None,
            "tags": None,
            "description": "Description",
            "availability": "In stock",
        },
        {
            "source": "Books to Scrape",
            "source_url": "book1",
            "name_or_title": "Book One",
            "category": "Fiction",
            "price": 10.0,
            "rating": 4,
            "author": None,
            "tags": None,
            "description": "Description",
            "availability": "In stock",
        },
    ])

    result = remove_duplicates(data)

    assert len(result) == 1


def test_remove_duplicate_quotes():
    data = pd.DataFrame([
        {
            "source": "Quotes to Scrape",
            "source_url": "quotes",
            "name_or_title": "Life is beautiful.",
            "category": None,
            "price": None,
            "rating": None,
            "author": "Author One",
            "tags": "life",
            "description": None,
            "availability": None,
        },
        {
            "source": "Quotes to Scrape",
            "source_url": "quotes",
            "name_or_title": "Life is beautiful.",
            "category": None,
            "price": None,
            "rating": None,
            "author": "Author One",
            "tags": "life",
            "description": None,
            "availability": None,
        },
    ])

    result = remove_duplicates(data)

    assert len(result) == 1


def test_output_files_exist():
    assert os.path.exists("output/books.csv")
    assert os.path.exists("output/quotes.csv")
    assert os.path.exists("output/consolidated_data.csv")
    assert os.path.exists("output/consolidated_data.json")
    assert os.path.exists("output/summary_metrics.json")


def test_books_output_count():
    books = pd.read_csv("output/books.csv")
    assert len(books) == 1000


def test_quotes_output_count():
    quotes = pd.read_csv("output/quotes.csv")
    assert len(quotes) == 100


def test_consolidated_output_count():
    data = pd.read_csv("output/consolidated_data.csv")
    assert len(data) == 1100