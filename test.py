import csv
from jobspy import scrape_jobs
import pandas as pd


jobs = scrape_jobs(
    site_name=["indeed", "linkedin"], # works for israel
    # "bayt", "naukri", "bdjobs", "zip_recrutier","glassdoor", "google"
    search_term="software engineer",
    job_level= "junior",
    # job_type="internship",
    # google_search_term="software engineer jobs near San Francisco, CA since yesterday",
    location="Tel Aviv , israel",
    distance=30,
    results_wanted=50,
    hours_old=168,
    country_indeed='israel',
    linkedin_fetch_description=True, # gets more info such as description, direct job url (slower)
    proxies=["localhost"]
)

# Check all jobs for 'job_type'
job_type_missing = jobs['job_type'].isna()  # True where job_type is missing
print(f"Jobs with missing job_type: {job_type_missing.sum()}/{len(jobs)}")

# Count missing job_type per site
missing_job_type_per_site = jobs[jobs['job_type'].isna()].groupby('site').size()

print("Missing job_type per site:")
print(missing_job_type_per_site)


# Show unique values for job_type
print("Unique job_type values:", jobs['job_type'].unique())
linkedin = jobs[jobs['site'] == "linkedin"]
indeed = jobs[jobs['site'] == "indeed"]


if "job_level" in linkedin.columns:
    linkedin_job_level_missing = linkedin['job_level'].isna()
    print(f"LinkedIn jobs with missing job_level: {linkedin_job_level_missing.sum()}/{len(linkedin)}")
    print("LinkedIn job_level values:", linkedin['job_level'].unique())
else:
    print("No 'job_level' column found in LinkedIn jobs")

print(f"found {len(jobs)} jobs")
linkedin_entry = linkedin[linkedin["job_level"].isin(["entry level","junior"])]
indeed_entry = indeed[indeed["job_level"] == "entry level"]
print(f"found {len(linkedin_entry)} linkedin entry level/junior jobs")


jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel


