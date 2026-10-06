import json
import logging
import os

import pandas as pd


# ==========================================
# CONFIGURATION
# ==========================================

BOOKS_FILE = "output/books.csv"
QUOTES_FILE = "output/quotes.csv"

CONSOLIDATED_CSV = "output/consolidated_data.csv"
CONSOLIDATED_JSON = "output/consolidated_data.json"
SUMMARY_FILE = "output/summary_metrics.json"

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
# COMMON SCHEMA
# ==========================================

COMMON_COLUMNS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "availability"
]


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(value):

    if pd.isna(value):
        return None

    value = str(value)

    value = " ".join(value.split())

    if value.strip() == "":
        return None

    return value.strip()


# ==========================================
# CLEAN PRICE
# ==========================================

def clean_price(value):

    if pd.isna(value):
        return None

    value = str(value)

    value = (
        value
        .replace("£", "")
        .replace("Â", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)

    except (ValueError, TypeError):
        return None


# ==========================================
# CLEAN RATING
# ==========================================

def clean_rating(value):

    if pd.isna(value):
        return None

    try:

        rating = float(value)

        if 0 <= rating <= 5:
            return rating

        return None

    except (ValueError, TypeError):
        return None


# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    dataframes = []

    # --------------------------------------
    # Books
    # --------------------------------------

    if os.path.exists(BOOKS_FILE):

        books_df = pd.read_csv(
            BOOKS_FILE
        )

        dataframes.append(
            books_df
        )

        logging.info(
            f"Loaded books data: {len(books_df)} records"
        )

        print(
            f"Books records loaded: {len(books_df)}"
        )

    else:

        logging.warning(
            f"Books file not found: {BOOKS_FILE}"
        )

        print(
            f"Warning: Books file not found: {BOOKS_FILE}"
        )

    # --------------------------------------
    # Quotes
    # --------------------------------------

    if os.path.exists(QUOTES_FILE):

        quotes_df = pd.read_csv(
            QUOTES_FILE
        )

        dataframes.append(
            quotes_df
        )

        logging.info(
            f"Loaded quotes data: {len(quotes_df)} records"
        )

        print(
            f"Quotes records loaded: {len(quotes_df)}"
        )

    else:

        logging.warning(
            f"Quotes file not found: {QUOTES_FILE}"
        )

        print(
            f"Warning: Quotes file not found: {QUOTES_FILE}"
        )

    if not dataframes:

        raise FileNotFoundError(
            "No input CSV files were found."
        )

    return dataframes


# ==========================================
# STANDARDIZE COLUMNS
# ==========================================

def standardize_columns(dataframes):

    standardized = []

    for dataframe in dataframes:

        dataframe = dataframe.copy()

        # Add missing columns
        for column in COMMON_COLUMNS:

            if column not in dataframe.columns:

                dataframe[column] = None

        # Keep only common schema
        dataframe = dataframe[
            COMMON_COLUMNS
        ]

        standardized.append(
            dataframe
        )

    return standardized


# ==========================================
# CLEAN DATA
# ==========================================

def clean_data(dataframe):

    dataframe = dataframe.copy()

    text_columns = [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "author",
        "tags",
        "description",
        "availability"
    ]

    for column in text_columns:

        dataframe[column] = dataframe[column].apply(
            clean_text
        )

    dataframe["price"] = dataframe["price"].apply(
        clean_price
    )

    dataframe["rating"] = dataframe["rating"].apply(
        clean_rating
    )

    return dataframe


# ==========================================
# VALIDATE REQUIRED FIELDS
# ==========================================

def validate_data(dataframe):

    required_columns = [
        "source",
        "source_url",
        "name_or_title"
    ]

    print("\nValidation Results:")

    for column in required_columns:

        missing_count = int(
            dataframe[column].isna().sum()
        )

        if missing_count == 0:

            print(
                f"  ✓ {column}: No missing values"
            )

        else:

            print(
                f"  ⚠ {column}: {missing_count} missing values"
            )

            logging.warning(
                f"{column} has {missing_count} missing values"
            )


# ==========================================
# REMOVE DUPLICATES
# ==========================================

def remove_duplicates(dataframe):

    before_count = len(dataframe)

    # --------------------------------------
    # Separate Books and Quotes
    # --------------------------------------

    books = dataframe[
        dataframe["source"] == "Books to Scrape"
    ].copy()

    quotes = dataframe[
        dataframe["source"] == "Quotes to Scrape"
    ].copy()

    # --------------------------------------
    # Books Duplicate Detection
    #
    # Each book has its own detail-page URL.
    # --------------------------------------

    books = books.drop_duplicates(
        subset=[
            "source_url"
        ],
        keep="first"
    )

    # --------------------------------------
    # Quotes Duplicate Detection
    #
    # Multiple quotes can exist on the same
    # page, so source_url cannot be used.
    # --------------------------------------

    quotes = quotes.drop_duplicates(
        subset=[
            "name_or_title",
            "author"
        ],
        keep="first"
    )

    # --------------------------------------
    # Combine Again
    # --------------------------------------

    dataframe = pd.concat(
        [
            books,
            quotes
        ],
        ignore_index=True
    )

    after_count = len(dataframe)

    duplicates_removed = (
        before_count - after_count
    )

    print(
        f"\nDuplicates removed: {duplicates_removed}"
    )

    logging.info(
        f"Duplicates removed: {duplicates_removed}"
    )

    return dataframe


# ==========================================
# GENERATE SUMMARY
# ==========================================

def generate_summary(dataframe):

    summary = {

        "total_records": int(
            len(dataframe)
        ),

        "records_by_source": {
            str(key): int(value)
            for key, value in dataframe[
                "source"
            ].value_counts().items()
        },

        "missing_values": {
            str(key): int(value)
            for key, value in dataframe.isna().sum().items()
            if value > 0
        },

        "duplicate_records": 0,

        "average_book_price": None,

        "average_book_rating": None
    }

    # --------------------------------------
    # Check duplicates separately
    # --------------------------------------

    books = dataframe[
        dataframe["source"] == "Books to Scrape"
    ]

    quotes = dataframe[
        dataframe["source"] == "Quotes to Scrape"
    ]

    book_duplicates = books.duplicated(
        subset=["source_url"]
    ).sum()

    quote_duplicates = quotes.duplicated(
        subset=[
            "name_or_title",
            "author"
        ]
    ).sum()

    summary["duplicate_records"] = int(
        book_duplicates + quote_duplicates
    )

    # --------------------------------------
    # Average Book Price
    # --------------------------------------

    prices = dataframe[
        dataframe["price"].notna()
    ]["price"]

    if not prices.empty:

        summary["average_book_price"] = round(
            float(prices.mean()),
            2
        )

    # --------------------------------------
    # Average Book Rating
    # --------------------------------------

    ratings = dataframe[
        dataframe["rating"].notna()
    ]["rating"]

    if not ratings.empty:

        summary["average_book_rating"] = round(
            float(ratings.mean()),
            2
        )

    return summary


# ==========================================
# SAVE OUTPUT
# ==========================================

def save_output(dataframe, summary):

    # --------------------------------------
    # CSV
    # --------------------------------------

    dataframe.to_csv(
        CONSOLIDATED_CSV,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\n✓ CSV created: {CONSOLIDATED_CSV}"
    )

    # --------------------------------------
    # JSON
    # --------------------------------------

    dataframe.to_json(
        CONSOLIDATED_JSON,
        orient="records",
        indent=4,
        force_ascii=False
    )

    print(
        f"✓ JSON created: {CONSOLIDATED_JSON}"
    )

    # --------------------------------------
    # Summary JSON
    # --------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"✓ Summary created: {SUMMARY_FILE}"
    )


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "       DATA PROCESSING PIPELINE"
    )

    print(
        "========================================"
    )

    logging.info(
        "Data processing started"
    )

    try:

        # 1. Load data
        dataframes = load_data()

        # 2. Standardize columns
        dataframes = standardize_columns(
            dataframes
        )

        # 3. Combine datasets
        combined_df = pd.concat(
            dataframes,
            ignore_index=True
        )

        print(
            f"\nRecords before cleaning: {len(combined_df)}"
        )

        # 4. Clean data
        combined_df = clean_data(
            combined_df
        )

        # 5. Validate data
        validate_data(
            combined_df
        )

        # 6. Remove duplicates
        combined_df = remove_duplicates(
            combined_df
        )

        # 7. Generate summary
        summary = generate_summary(
            combined_df
        )

        # 8. Save outputs
        save_output(
            combined_df,
            summary
        )

        # ==================================
        # FINAL RESULT
        # ==================================

        print(
            "\n========================================"
        )

        print(
            "       PROCESSING COMPLETED"
        )

        print(
            "========================================"
        )

        print(
            f"Total records: {len(combined_df)}"
        )

        print(
            "\nRecords by source:"
        )

        for source, count in summary[
            "records_by_source"
        ].items():

            print(
                f"  {source}: {count}"
            )

        print(
            f"\nAverage price: "
            f"{summary['average_book_price']}"
        )

        print(
            f"Average rating: "
            f"{summary['average_book_rating']}"
        )

        logging.info(
            "Data processing completed successfully"
        )

    except Exception as error:

        logging.exception(
            f"Data processing failed: {error}"
        )

        print(
            f"\nERROR: {error}"
        )