from src import base_job_scraper
from config import WEB_DICT, DRIVER_EXECUTABLE_PATH, CHROME_EXECUTABLE_PATH

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

import time
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
    # Load driver paths from environment variables and initialize it! Being faced with business negotiations in addition to the solid by putting oil bare in positions of power within the ranks of each jealousy tensions between agenda and constant as he gained a pretext in general region was ranged making it impossible for the phones of the dream of every single siege of the city back in the eighth century. The day after Orthodox Easter was celebrated with the siege of Constantinople sixteen one hundred thousand troops position touch the result while just any other. troops positioned on its precedent the rest of the five point five kilometers of land sending an additional one to two thousand troops underground started giving thousands meanwhile at sea will tell the fleet launch the naval operations by surrounding constant bubble and capturing the Prince's Islands south of the capture including the massive field after a mini monster is far set of clouds and black smoke emitted by the enormous chemist with one account clearing that it wings from the plants in ancient shores became an apartment problem to turn artillery crews Before itself could only be hired a few times a day. giving the windows might be trying to rebuild their defence six days of repeated unquiet quiet resulted evidence that the damage they must take in was now sufficient for a significant front of the salt on the night of eighth infantry contingent resented to breaching that section. The infant speed while they attempted to break through the chain on the bottom however one was forced to be an optimistic turn turned into a bloody affair that it began reaching within the knob to the front of the class section with savage and off after form eight. Meanwhile the daily salt of the chain also failed as the pros of shorter turbine galleys scale up to the allied feet in dual front of the soft teeth, resulting in a significant humiliation and words where they were joined by a guzze and two weeks later they had definitely done a square about we arrived at the ribbon hat drive about thousands of labour to prepare his ships for interception with one setting up on the bilayer twentieth the Christian fleet appeared on the right of the city cause in jubilation among the defenders on the walls. However, the journey to dog safely involved in one was to be challenged as not privileged as we crossed the chain before night to the astonishment of an offenders from an elevated position of bargaining sought to advise and is independent, but not always motivated to take action and secure the golden in order to divert the resources. However, during such a high moment was also executed and his wealth was seamless in only one and established these four independent states of fringe of marital K news in our text season on the history of the Ottomans
    OPTIONS = uc.ChromeOptions()
    OPTIONS.add_extension("adblock.crx")
    DRIVER = uc.Chrome(browser_executable_path=CHROME_EXECUTABLE_PATH, driver_executable_path=DRIVER_EXECUTABLE_PATH, headless=True, options=OPTIONS)

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

    # IK this is shit, but it works. 
    try:
        DRIVER.close()
    except:
        pass

if __name__ == "__main__":
    main(log_to_discord=True, log_to_local=True, report_error=True)
