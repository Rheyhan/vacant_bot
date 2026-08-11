# Unofficial API for Disnakerja, Inginkerja, & RekrutmenBersama

An automated job vacancy scraper, wrangler, and evaluation tool that aggregates recent listings from Disnakerja, Inginkerja, and RekrutmenBersama.

## Overview & Motivation

This project was firstly built as a personal job-hunting automation tool designed to:
- Automatically scrape and wrangle job postings from Indonesian job portals every 4 hours.
- Evaluate and filter job requirements against a Resume / CV using the Google Gemini API.
- Dispatch high-matching alerts to Discord and save processed listings to a database.
- Serve clean job data via a public REST API endpoint.

## API Endpoint
Recent Jobs Endpoint: http://api-vb.rheyhan.com/all/recent

## AI Assisted Job Search with endpoint data
Please do note, 

## Pipeline Workflow
```
[ Scraper / Wrangler ] ──> [ Gemini AI Evaluation ] ──> [ Discord Alert / SQL DB ] ──> [ REST API ]
  (data_fetcher.py)             (gemini_functions)           (sql_functions)           (endpoint.py)
```
Fetch Data: Extracts raw job listings from target portals using headless browser/requests with adblock (adblock.crx).
AI Wrangling: Evaluates job descriptions against CV criteria using Gemini API to determine suitability.
Database & Alerts: Persists qualified listings to SQL, logs activity (online_logs.py), and fires notifications.
API Service: Serves recent job data via endpoint.py.

## Project Structure
```
├── utils/                   # Helper modules and utilities
│   ├── __pycache__/
│   ├── URL_LOG_Funcs.py     # URL tracking and logging functions
│   ├── gemini_functions.py  # AI suitability checking via Gemini API
│   ├── online_logs.py       # Cloud/online logging utilities
│   └── sql_functions.py     # Database interaction modules
├── adblock.crx              # Browser extension for blocking ads during scraping
├── config.py                # Configuration and environment variables
├── data_fetcher.py          # Core scraping and data wrangling script
├── endpoint.py              # API routing and server logic
├── readme.MD                # Project documentation
├── requirements.txt         # Python dependencies
└── src.py                   # Main pipeline execution script
```

## Setup and Installation, if you want to run this project locally

1. Clone the Repository
```{bash}
git clone https://github.com/your-username/repository-name.git
cd repository-name
```

2. Install Dependencies
```{bash}
pip install -r requirements.txt
```

3. Configuration
Configure your environment variables inside config.py:
- Gemini API Key: For CV relevance parsing.
- Discord Webhook URL: For automated job alerts.
- Database Credentials: For saving scraped and filtered listings.

4. Running the Application
- Run the main automation pipeline (Scrape -> Evaluate -> Push):
```{bash}
python src.py
```

- Start the REST API server:
```{bash}
python endpoint.py
```