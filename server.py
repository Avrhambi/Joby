import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from jobspy import scrape_jobs
import pandas as pd
from fastapi import FastAPI, Query
from jobspy import scrape_jobs
from typing import List, Literal
from pydantic import BaseModel

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class JobSearchRequest(BaseModel):
    job_titles: List[str]                
    seniority: Literal["junior", "senior", "chief"]
    country: str
    location: str
    city: str                        
    job_scope: Literal["part time", "full time"]
    frequency: Literal["twice_day", "daily", "every_two_days", "weekly"]


app = FastAPI(
    title="Jobs Search",
    description="A dedicated API server for Jobs Search",
    version="1.0"
)

@app.get("/")
def root():
    return {"message": "JobSpy API is running!"}





@app.get("/jobs_search")
def search_jobs(request: JobSearchRequest):
    job_titles = request.job_titles
    area = request.location  # the “area” field
    city = request.city
    all_jobs_dfs = []

    # Helper function to scrape jobs for a single title
    def fetch_jobs(title, site):
        try:
            if site == "indeed":
                loc = area
            else:  # linkedin
                loc = f"{area}, {city}"

            jobs = scrape_jobs(
                site_name=[site],
                search_term=title,
                location=loc,
                results_wanted=10,
                hours_old=168,
                country_indeed='Israel'
            )
            return jobs
        except Exception as e:
            print(f"Error scraping {title} on {site}: {e}")
            return pd.DataFrame()


    # Run scraping in parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_jobs, title) for title in job_titles]
        for future in as_completed(futures):
            df = future.result()
            if not df.empty:
                all_jobs_dfs.append(df)

    if not all_jobs_dfs:
        return {"count": 0, "jobs": []}

    # Combine all DataFrames and sort by date_posted
    all_jobs_df = pd.concat(all_jobs_dfs, ignore_index=True)
    if "date_posted" in all_jobs_df.columns:
        all_jobs_df.sort_values(by="date_posted", ascending=False, inplace=True)

    # Convert to list of dicts for JSON response
    jobs_list = all_jobs_df.to_dict(orient="records")
    return {"count": len(jobs_list), "jobs": jobs_list}

    



