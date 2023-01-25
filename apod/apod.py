"""Module providingFunction printing python version."""
import random
from datetime import datetime
import os
import requests
import sys

def random_date():
    """
    "random" to get one date from 2015-01-01 to today
    Returns:
        date(str)
    """
    start_date = datetime.today().replace(day=1, month=1, year=2015).toordinal()
    end_date = datetime.today().toordinal()
    return datetime.fromordinal(random.randint(start_date, end_date)).strftime("%Y-%m-%d")

def download_image(url, file_path):
    """
    Image Download
        Args:
            url(str): image url
            file_path(str): path to save
    """
    os.system("curl " + url + " > " + file_path)

def fetch_apod(date):
    """
    Call APOD API
        Args:
            date(str) : date
    """
    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {
        'api_key':os.environ.get('APOD_API_KEY'),
        'date':date,
        'hd':'True'
    }
    response = requests.get(apod_url, params=params, timeout=5).json()
    return response["hdurl"]


def main():
    """
    Main function
    """
    file_path = " ".join(sys.argv[1:len(sys.argv)])
    hdurl = fetch_apod(random_date())
    download_image(hdurl, file_path)

if __name__ == "__main__":
    main()