# this is the main scraper for 104 job postings, it will scrape the job postings from 104 
# and return a list of job postings with the following details: 
# source_job_id, job_title, company, raw_location, experience, remote, salary_min, salary_max
import requests
from loguru import logger
from .functions import extract_104_id

def scrape_104_jobs(search_term="資料工程師", page="1"):
    based_url = "https://www.104.com.tw/jobs/search/api/jobs"

    # define the parameters for the GET request
    params = {
        "asc": 1,
        "jobsource": "joblist_search",
        "keyword": search_term,
        "mode": "s",
        "order": 4,
        "page": page,  # Inject the current page number
        "pagesize": 20,
        "searchJobs": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
    }
    # for storing the results
    job_postings = []

    try:
        response = requests.get(based_url, params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error occurred while making the request: {e}")
        # let Celery retry automatically 
        raise
    if response.status_code != 200:
        logger.warning(f'Status code {response.status_code} received for page {page}, term "{search_term}".')
        return None
    # parsing level failure -> change in the response 
    try:
        data = response.json()['data']
    except (KeyError, ValueError):
        logger.exception(f'Unexpected response shape from 104 on page {page}, term "{search_term}".')
        return None
    # extract the data
    data = response.json()["data"]
    # print(data)   
    for job in data:
        try:
            details = {
                "source_job_id": extract_104_id(job["link"]["job"]),
                "job_title": job["jobName"],
                "company": job["custName"],
                # raw location = city + district
                "raw_location": job["jobAddrNoDesc"],
                "experience": job["jobRo"] if "jobRo" in job else None,
                "remote":job["remoteWorkType"] if "remoteWorkType" in job else None,
                "salary_min": job["salaryLow"] if "salaryLow" in job else None,
                "salary_max": job["salaryHigh"] if "salaryHigh" in job else None,
                "detail_status": "pending" # default value for detail_status, will be updated later when fetching job details
            }
            job_postings.append(details)
        except KeyError as e:
            logger.warning(f"Skipped a job posting due to missing key: {e} on page {page}")
            continue
    if not job_postings:
        return None
    return job_postings

print(scrape_104_jobs())