# AI Usage Documentation

## Overview

AI assistance was used during the development of this web scraping project to support coding, debugging, testing, documentation, and problem solving.

The final implementation was reviewed, tested, and executed locally before submission.

---

## Areas Where AI Assistance Was Used

### 1. Project Structure

AI assistance was used to plan and organize the project structure into separate modules for:

- Books scraping
- Quotes scraping
- Data processing
- Automated testing
- Logging
- Output files

The final project structure was reviewed and implemented locally.

---

### 2. Web Scraper Development

AI assistance helped with developing the initial scraper logic using:

- Python
- Requests
- BeautifulSoup
- Pagination handling
- HTTP request handling
- Retry mechanisms
- Data extraction

The scraper implementation was then executed and tested locally.

---

### 3. Data Cleaning and Processing

AI assistance was used to design the data processing pipeline.

The processing pipeline performs:

- Text cleaning
- Price normalization
- Rating normalization
- Required field validation
- Duplicate detection
- Data consolidation
- CSV generation
- JSON generation
- Summary metric generation

The resulting pipeline was executed locally and verified using the generated outputs.

---

### 4. Debugging

AI assistance was used to identify and resolve development issues, including:

- Incorrect price encoding such as `Â£`
- Duplicate detection logic
- Python package import errors
- Test configuration issues

Each fix was tested locally after implementation.

---

### 5. Automated Testing

AI assistance was used to create pytest test cases covering:

- Text cleaning
- Price cleaning
- Rating validation
- Book duplicate detection
- Quote duplicate detection
- Output file existence
- Books record count
- Quotes record count
- Consolidated record count

The final test execution produced:

```text
9 passed