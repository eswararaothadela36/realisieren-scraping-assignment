# Realisieren Technologies - Python Web Scraping Assignment

## Project Overview

This project implements a production-oriented Python web scraping pipeline for extracting, cleaning, validating, and consolidating data from:

1. Books to Scrape
2. Quotes to Scrape

The project includes separate scraper modules, pagination handling, retries, error handling, data processing, duplicate detection, logging, automated tests, and consolidated CSV/JSON outputs.

---

## Features

- Scrapes all available books from Books to Scrape
- Scrapes quotes from Quotes to Scrape
- Handles pagination
- Uses HTTP requests with timeouts
- Implements retry handling for failed requests
- Extracts data from detail pages where required
- Cleans and normalizes scraped data
- Validates required fields
- Detects and removes duplicate records
- Produces consolidated CSV and JSON files
- Generates summary metrics
- Maintains application logs
- Includes automated pytest tests

---

## Project Structure

```text
realisieren_scraping_assignment/
│
├── logs/
│   └── scraper.log
│
├── output/
│   ├── books.csv
│   ├── quotes.csv
│   ├── consolidated_data.csv
│   ├── consolidated_data.json
│   └── summary_metrics.json
│
├── processing/
│   ├── __init__.py
│   └── data_processor.py
│
├── scrapers/
│   ├── __init__.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
│
├── tests/
│   ├── __init__.py
│   └── test_scrapers.py
│
├── requirements.txt
├── README.md
└── AI_USAGE.md