from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI
from jobspy import scrape_jobs
from pydantic import BaseModel
from typing import Literal
import pandas as pd
from datetime import datetime
import math
import json

app = FastAPI()

# -------------------------------
# Request Model
# -------------------------------
class JobSearchRequest(BaseModel):
    title: str
    seniority: Literal["intern","junior", "senior", "chief"]
    country: str
    location: str  # city or district
    dist: int  # distance
    job_scope: Literal["parttime", "temporary", "fulltime"]
    days_back: int  # how many days to look back


# -------------------------------
# Map Israeli districts → representative cities
# -------------------------------
DISTRICT_TO_CITY = {
    "center district": "Tel Aviv",
    "north district": "Haifa",
    "south district": "Be'er sheva",
    "hasharon district": "Natanya",
}


# -------------------------------
# Infer job level if missing
# -------------------------------
def infer_job_level(row, job_level):
    text = f"{row.get('title', '')} {row.get('job_url_direct', '')}".lower()

    keywords = {
        "intern": ["intern", "internship", "student"],
        "junior": ["junior", "jr", "entry level", "grad"],
        "senior": ["senior", "sr"],
        "chief": ["chief"]
    }

    # Get only the keywords for the given job_level
    target_keywords = keywords.get(job_level.lower(), [])

    # If any of those keywords appear in the text — return that level
    if any(k in text for k in target_keywords):
        return job_level
        
    return None

def clean_nans(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces NaN, None, inf, -inf values in a DataFrame with empty strings,
    making it safe to convert to JSON.
    """
    pd.set_option('future.no_silent_downcasting', True)
    df = df.replace([float("inf"), float("-inf")], "")
    df = df.fillna("")  # replace NaN/None with empty string
    return df



# -------------------------------
# Main Endpoint
# -------------------------------
@app.post("/jobs_search")
def search_jobs(request: JobSearchRequest):
    title = request.title
    country = request.country
    location = request.location
    seniority = request.seniority
    days_back = request.days_back
    dist = request.dist
    job_scope = request.job_scope

    # Replace district with representative city (for Indeed)
    indeed_loc = DISTRICT_TO_CITY.get(location.lower())
    linkedin_loc = location  

    # ---------------------------
    # Helper: fetch jobs per site
    # ---------------------------
    def fetch_jobs(site):
        try:
            loc = indeed_loc if (indeed_loc and  site == "indeed") else linkedin_loc
            term = f"{title}" if site == "indeed" else f"{seniority} {title}"
            jobs = scrape_jobs(
                site_name=[site],
                search_term=term,
                location=f"{loc}, {country}",
                distance=dist,
                job_type=job_scope,
                job_level = seniority,
                results_wanted=50,  # fetch more for filtering
                hours_old=24 * days_back,
                country_indeed=country,
                linkedin_fetch_description=True, # gets more info such as description, direct job url (slower)
                proxies=["localhost"]
            )

            if jobs.empty:
                return pd.DataFrame()


            # Infer missing job levels
            jobs["job_level"] = jobs.apply(
                lambda r: r["job_level"] if pd.notnull(r.get("job_level")) else infer_job_level(r, seniority),
                axis=1
            )

            # ---------------------------
            # Filtering logic
            # ---------------------------'
            if seniority == "junior":
                mask = (
                    (jobs["job_level"] == "entry level") |
                    (jobs["job_level"].str.contains("junior", case=False, na=False))
                )
                jobs = jobs[mask]
 
            elif seniority == "intern":
                mask = (
                        jobs["job_type"].str.contains("intern|internship", case=False, na=False) |
                        jobs["job_level"].str.contains("intern", case=False, na=False)
                    )
                jobs = jobs[mask]

            elif seniority == "senior":
                mask = (
                        jobs["job_level"].isna() |
                        jobs["job_level"].str.contains("senior", case=False, na=False)
                    )
                jobs = jobs[mask]

            # if seniority == "junior":
            #     jobs= jobs[( (jobs[jobs["job_level"] == "entry level"]) 
            #             |  (jobs[jobs["job_level"].str.contains("junior", case=False, na=False)]) )]
            # elif seniority == "intern":
            #     jobs = jobs[((jobs[jobs["job_type"].str.contains("intern|internship", case=False, na=False)]) 
            #         | (jobs["job_level"].str.contains("intern", case=False, na=False)))]
            # elif seniority == "senior":
            #     jobs = jobs[
            #        ( (jobs["job_level"].isna())
            #         | (jobs["job_level"].str.contains("senior", case=False, na=False)))
            #     ]
            # elif seniority == "chief":
            #     jobs = jobs[jobs["job_level"].str.contains("chief", case=False, na=False)]

            # Sort by most recent
            if "date_posted" in jobs.columns:
                jobs.sort_values(by="date_posted", ascending=False, inplace=True)

            return jobs

        except Exception as e:
            print(f"Error scraping {site}: {e}")
            return pd.DataFrame()

    # ---------------------------
    # Run in parallel (Indeed + LinkedIn)
    # ---------------------------
    sites = ["indeed", "linkedin"]
    all_jobs_df = {}

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_jobs, site): site for site in sites}
        for future in as_completed(futures):
            site = futures[future]
            df = future.result()
            if not df.empty:
                all_jobs_df[site] = df

    # ---------------------------
    # Merge & Fill Logic
    # ---------------------------
    if not all_jobs_df:
        return {"count": 0, "indeed_count": 0, "linkedin_count": 0, "jobs": []}

    indeed_jobs = all_jobs_df.get("indeed", pd.DataFrame())
    linkedin_jobs = all_jobs_df.get("linkedin", pd.DataFrame())

    # Desired per-site quota
    TARGET_PER_SITE = 5
    TOTAL_TARGET = 10

    # Count how many jobs we got from each site
    indeed_count = len(indeed_jobs)
    linkedin_count = len(linkedin_jobs)

    # Case 1: Both have enough
    if indeed_count >= TARGET_PER_SITE and linkedin_count >= TARGET_PER_SITE:
        indeed_jobs = indeed_jobs.head(TARGET_PER_SITE)
        linkedin_jobs = linkedin_jobs.head(TARGET_PER_SITE)

    # Case 2: Indeed has fewer than 5 → fill from LinkedIn
    elif indeed_count < TARGET_PER_SITE:
        missing = TARGET_PER_SITE - indeed_count
        linkedin_extra = linkedin_jobs.iloc[:TARGET_PER_SITE + missing]  # take more
        linkedin_jobs = linkedin_extra
        # Indeed stays as is (maybe 2–3 jobs only)

    # Case 3: LinkedIn has fewer than 5 → fill from Indeed
    elif linkedin_count < TARGET_PER_SITE:
        missing = TARGET_PER_SITE - linkedin_count
        indeed_extra = indeed_jobs.iloc[:TARGET_PER_SITE + missing]
        indeed_jobs = indeed_extra

    # Combine results
    all_jobs_df = pd.concat([indeed_jobs, linkedin_jobs], ignore_index=True)

    # sort by date_posted
    if "date_posted" in all_jobs_df.columns:
        all_jobs_df.sort_values(by="date_posted", ascending=False, inplace=True)


    # Limit total to 10
    all_jobs_df = all_jobs_df.head(TOTAL_TARGET)

    # Replace NaN/None values
    all_jobs_df = clean_nans(all_jobs_df)

    # Convert to JSON-safe format
    jobs_list = all_jobs_df.to_dict(orient="records")
    
    print(f"Returning {len(jobs_list)} jobs: Indeed={len(indeed_jobs)}, LinkedIn={len(linkedin_jobs)}")

    return {
        "count": len(all_jobs_df),
        "indeed_count": len(indeed_jobs),
        "linkedin_count": len(linkedin_jobs),
        "jobs": jobs_list
    }

@app.get("/")
def health_check():
    """
    Simple health check endpoint
    """
    return {"message":"jobs server is running", "timestamp": datetime.utcnow().isoformat()}