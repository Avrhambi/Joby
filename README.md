# Joby (jobs-engine)

This repository provides a small FastAPI service that uses the `jobspy` scraper to collect job listings (Indeed / LinkedIn), a sample CSV of scraped jobs (`jobs.csv`) and a few convenience test scripts.

## What this project does

- Exposes a FastAPI app in `main.py` with two endpoints:
	- `GET /` — health check
	- `POST /jobs_search` — search jobs by title, seniority, location, distance and other filters; returns consolidated results from Indeed and LinkedIn
- Contains example/test scripts: `api_test.py`, `data_test.py`, and `server_test.py`.
- Stores a sample export of job listings in `jobs.csv` (header shown below).

## Features

- Parallel scraping of multiple sites (Indeed, LinkedIn) and simple merge/quotas per site
- Basic inference and filtering for `job_level`, job type and date
- JSON-safe output (NaN/inf cleaned) and configurable fetch options via the `jobspy` wrapper

## Requirements

- Python 3.9+ (3.10/3.11 recommended)
- These Python packages (quick list):
	- fastapi
	- uvicorn
	- pandas
	- pydantic
	- jobspy
	- requests

Create a virtual environment and install the packages (example):

```powershell
# create & activate venv (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install dependencies (if you have a requirements.txt)
pip install -r requirements.txt

# or install the minimal set directly
pip install fastapi uvicorn pandas pydantic jobspy requests
```

Note: `jobspy` may require additional system dependencies or proxies depending on the sites you target. See the troubleshooting section below.

## Run the API server

Start the FastAPI server (the `app` object is defined in `main.py`):

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Health check:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8001/ -Method GET
```

Search endpoint example (curl):

```bash
curl -X POST http://127.0.0.1:8001/jobs_search \
	-H "Content-Type: application/json" \
	-d '{"title":"software engineer","seniority":"senior","country":"israel","location":"Tel Aviv","dist":20,"job_scope":"fulltime","days_back":2}'
```

Python example using `requests` (same payload used by `api_test.py`):

```python
import requests

url = "http://127.0.0.1:8001/jobs_search"
payload = {
		"title": "software engineer",
		"seniority": "senior",
		"country": "israel",
		"location": "Tel Aviv",
		"dist": 20,
		"job_scope": "fulltime",
		"days_back": 2
}

resp = requests.post(url, json=payload)
print(resp.status_code)
print(resp.json())
```

## `jobs.csv` schema

The repository includes a sample `jobs.csv`. The file header contains the following columns (exported by the scraper):

```
id,site,job_url,job_url_direct,title,company,location,date_posted,job_type,salary_source,interval,min_amount,max_amount,currency,is_remote,job_level,job_function,listing_type,emails,description,company_industry,company_url,company_logo,company_url_direct,company_addresses,company_num_employees,company_revenue,company_description,skills,experience_range,company_rating,company_reviews_count,vacancy_count,work_from_home_type
```

Fields of note:
- `site` — source site (e.g. `indeed`, `linkedin`)
- `job_url` / `job_url_direct` — listing URLs
- `date_posted` — date string used for sorting
- `job_level` and `job_type` — used for filtering (may be missing for some listings)
- `description` — full job description (may contain newlines and special characters)

When serving JSON, the code replaces NaN/inf with empty strings to ensure safe serialization.

## Tests and example scripts

- `data_test.py` — example script that calls `jobspy.scrape_jobs` and prints/saves results. Can be used to regenerate `jobs.csv`.
- `api_test.py` — small client that posts to the running `/jobs_search` endpoint. Use this after you start the server.
- `server_test.py` — additional checks for the server (health and example flows).

Run them like this:

```powershell
# scrape sample jobs locally
python data_test.py

# start server in another terminal, then run the API test
python api_test.py

# run server_test for quick health checks
python server_test.py
```

Note: some scripts call `jobspy` and may require a working proxy or site-specific configuration. If you encounter empty results, check that `jobspy` is configured and able to access the target sites.

## Troubleshooting

- If scrapes return empty DataFrames: ensure network connectivity, appropriate proxies and that target sites haven't blocked requests.
- `jobspy` may expose options like `proxies` and `linkedin_fetch_description` — tweak them in `main.py` or test scripts.
- For encoding issues when reading/writing `jobs.csv`, use UTF-8 and the Python `csv` module with appropriate quoting/escape settings (the sample CSV in this repo was exported with quoting and escaped characters).


