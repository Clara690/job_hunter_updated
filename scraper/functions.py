# here stores the functions used in the scraper module.
from urllib.parse import urlsplit

def extract_104_id(url: str) -> str | None:
    """
    Extracts the job ID from a 104 job URL.

    Args:
        url (str): The URL of the job posting.
    """
    job_id = urlsplit(url).path.split("/")[-1]  # Extract the last part of the path
    return job_id if job_id else None