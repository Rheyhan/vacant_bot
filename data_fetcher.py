from src import base_job_scraper
from config import WEB_DICT

import undetected_chromedriver as uc
import os
from typing import *
from dotenv import load_dotenv
load_dotenv()

def main(log_to_discord: bool = True, log_to_local: bool = True, report_error: bool = True):
    '''
    Main function to initiate the job scraping process.

    Parameters
    ----------
    log_to_discord : bool
        Whether to send the accepted vacancies to the Discord webhook (default: True)
    log_to_local : bool
        Whether to log the accepted vacancies to the local database (default: True)
    report_error : bool
        Whether to report errors via email (default: True)
    '''
    # Load driver paths from environment variables and initialize it!
    CHROME_EXECUTABLE_PATH = os.getenv("CHROME_EXECUTABLE_PATH", "D:/chrome-win64/chrome.exe")
    DRIVER_EXECUTABLE_PATH = os.getenv("DRIVER_EXECUTABLE_PATH", "D:/chromedriver-win64/chromedriver.exe")
    DRIVER = uc.Chrome(browser_executable_path=CHROME_EXECUTABLE_PATH, driver_executable_path=DRIVER_EXECUTABLE_PATH, headless=False)

    if report_error:
        from utils.online_logs import send_email
        EMAIL_CREDENTIALS = {
            "email": os.getenv("EMAIL"),
            "password": os.getenv("PASSWORD"),
            "send_to_email": os.getenv("SEND_TO_EMAIL")
        }
    if log_to_local:
        from utils.sql_functions import init_db
        init_db()

    for website in list(WEB_DICT.keys()):
        try:
            theProcess = base_job_scraper(DRIVER, local_log=log_to_local, discord_log=log_to_discord, website_loker=website)
            theProcess.start()
        except Exception as exc:
            print(f"Error in main: {exc}")
            if report_error:
                send_email(str(exc), EMAIL_CREDENTIALS)

    DRIVER.quit()

if __name__ == "__main__":
    main(log_to_discord=True, log_to_local=True, report_error=True)