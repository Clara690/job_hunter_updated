import requests
from loguru import logger

def fetch_job_details(job_id):
    based_url = f"https://www.104.com.tw/job/ajax/content/{job_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
    }
    job_details = {}
    try:
        response = requests.get(based_url, headers=headers)
        details = response.json()
        job_details = {
            "source_job_id": job_id,
            "date_posted": details.get('data', {}).get("appearDate"),
            "education": details["data"]["condition"]["edu"],
            "industry": details["data"]["industry"],
            "location": details["data"]["jobDetail"]["addressArea"],
            "job_description": details["data"]["jobDetail"]["jobDescription"],
        }
        return job_details
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error occurred while fetching job details for ID {job_id}: {e}")
        return None

print(fetch_job_details("8x352")) # Example usage with a sample job ID