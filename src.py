from utils.gemini_functions import verify_vacancy, parse_json_response
from utils.online_logs import send_post_on_discord
from utils.URL_LOG_Funcs import log_URLs, get_past_URLs
from utils.sql_functions import insert_rows

from config import WEB_DICT, MAX_PAST_DATE, API_TIMEOUT, LONG_WAIT, SHORT_WAIT

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import datetime
from typing import *
import dateparser

import os
from google import genai

from dotenv import load_dotenv
load_dotenv()
# Gemini API key and client initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GENAI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
# Discord webhook URL from environment variable
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

class base_job_scraper:
    def __init__(self, DRIVER, local_log: bool = True, discord_log: bool = False, 
                 website_loker: Literal["Disnakerja", "Inginkerja", "RekrutmenBersama"] = None):
        '''
        Initialize the base job scraper class.

        Parameters
        ----------
        - DRIVER : undetected_chromedriver.Chrome
            The undetected chromedriver instance to be used for web scraping.
        - local_log : bool
            Whether to log the accepted vacancies to the local database (default: True)
        - discord_log : bool
            Whether to send the accepted vacancies to the Discord webhook (default: False)
        - website_loker : Literal["Disnakerja", "Inginkerja", "RekrutmenBersama"]
            The job website to scrape (default: None)
        '''
        # For logging purposes
        self.accepted_vacancies = []
        self.all_vacancies = []
        self.temp_logged_URLs = []

        self.website_loker = website_loker
        self.search_status = 1  # Status to control the scraping loop, 1 means continue, 0 means stop

        # Store the latest URL to avoid re-scraping already processed job postings
        self.latest_url = get_past_URLs(self.website_loker)

        # Logging preferences, local will log to the local database, discord will send a message to the discord webhook
        self.local_log = local_log
        self.discord_log = discord_log

        self.DRIVER = DRIVER

    def get_vacancy_page(self):
        '''
        Scrape the job vacancy page and extract relevant information.

        This function will extract the company name, icon, view count, last updated date, location, experience needed, and job description from the job vacancy page.

        It will also verify if the vacancy is suitable for the applicant using the Gemini API and log the accepted vacancies to the local database and/or send them to the Discord webhook based on the logging preferences.
        '''
        # For a page
        content = WebDriverWait(self.DRIVER, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'content-area']")))

        # Get the top content of the job listing
        top_content = content.find_element(By.XPATH, ".//header")
        icon = top_content.find_element(By.XPATH, ".//img").get_attribute("src")
        nama_perusahaan = top_content.find_element(By.XPATH, ".//h1[@itemprop='name']").text

        # Get the lower content of the job listing
        lower_content = content.find_element(By.XPATH, ".//div[@class='row']")
        side_content = lower_content.find_element(By.XPATH, ".//div[@id='specs']")
        side_content_text = side_content.text
        jobdescription = lower_content.find_element(By.XPATH, ".//div[@id='description']").text
        side_content_parsed = [line.strip() for line in side_content_text.split('\n') if line.strip()]

        # Extracting specific details from the parsed side content based on the website
        match self.website_loker:
            case "Disnakerja":
                view_count = top_content.find_element(By.XPATH, ".//span[@class='gmr-view']").text

                last_updated = side_content_parsed[1]
                location = side_content_parsed[6]
                experience_needed = side_content_parsed[12]
                # work_type = side_content_parsed[8]
                # required_education = side_content_parsed[10]
                # category = side_content_parsed[3]

            case "Inginkerja":
                view_count = "No info"
                last_updated = side_content_parsed[3]
                location = side_content_parsed[8]
                experience_needed = "No info"

            case "RekrutmenBersama":
                view_count = "No info"
                last_updated = side_content_parsed[1]
                location = side_content_parsed[7]
                experience_needed = "No info"

        # Convert the last updated date from Indonesian to English month names for proper date parsing
        parsed_datetime = dateparser.parse(last_updated)
        
        if parsed_datetime:
            last_updated_date_object = parsed_datetime.date()
        else:
            last_updated_date_object = self.all_vacancies[-1]["Last_Updated"] if self.all_vacancies else datetime.datetime.now().date()

        # Stop if the job posting is older than the maximum allowed days
        if last_updated_date_object < MAX_PAST_DATE:
            self.search_status = 0
            return None
        
        # Verify if the vacancy is suitable for the applicant using the Gemini API
        Full_job_description = side_content_text + "\n" + jobdescription
        status = 0
        while not status:
            response, status = verify_vacancy(GENAI_CLIENT, Full_job_description)
            if not status:
                time.sleep(API_TIMEOUT) # Try to get it indefinitely until the API is available.

        acceptance, position, reason = parse_json_response(response) # Safely parse the response to get acceptance, position, and reason from json the format

        # Change position column to a string, bcz it's a list
        position = ", ".join(position) if isinstance(position, list) else position

        # print(f"Reason: {reason}")

        # If the vacancy is accepted
        if acceptance == "1":
            returned_job = {
                "Nama_Perusahaan": nama_perusahaan,
                "Icon": icon, 
                "View_Count": view_count,
                "Last_Updated": str(last_updated_date_object),
                "Location": location,
                "Experience_Needed": experience_needed,
                "Position": position,
                "Reason": reason,
                "Post_link": self.DRIVER.current_url,
                "Website_Loker": self.website_loker
            }
            if self.discord_log:
                send_post_on_discord(returned_job, DISCORD_WEBHOOK_URL)
                
            self.accepted_vacancies.append(returned_job)

        # Overall logs, doesn't matter if the vacancy is accepted or not, js log it
        overall_log = {
            "Nama_Perusahaan": nama_perusahaan,
            "View_Count": view_count,
            "Last_Updated": str(last_updated_date_object),
            "Location": location,
            "Experience_Needed": experience_needed,
            "Position": position,
            "Post_link": self.DRIVER.current_url,
            "Website_Loker": self.website_loker,
            "DESCRIPTION": Full_job_description,
        }

        self.all_vacancies.append(overall_log)

    def start(self, current_page: int = 1) -> tuple:
        '''
        Start the job scraping process for the specified job website.

        Parameters
        ----------
        - current_page : int
            The page number to start scraping from (default: 1)

        Returns
        -------
        - self.accepted_vacancies : list
            A list of accepted vacancies that match the applicant's profile
        - self.all_vacancies : list
            A list of all vacancies that were scraped, regardless of acceptance
        '''

        # Get the base URL for the specified job website
        Used_URL = WEB_DICT[self.website_loker]

        while self.search_status:
            self.DRIVER.get(Used_URL + str(current_page))

            # Wait for the job board to load
            try:
                job_board = WebDriverWait(self.DRIVER, LONG_WAIT).until(EC.presence_of_element_located((By.ID, "gmr-main-load")))
            except:
                job_board = None
                return self.accepted_vacancies, self.all_vacancies

            # Get all job listings on the current page and their links
            job_lists = job_board.find_elements(By.XPATH, "//article")
            job_link_lists = [job.find_element(By.XPATH, ".//h2/a").get_attribute("href") for job in job_lists]

            # Process each link
            for link in job_link_lists:
                if link == self.latest_url:
                    self.search_status = 0  # Stop the search if the latest URL is reached
                    break

                self.DRIVER.get(link)
                self.temp_logged_URLs.append(link)  # Log the URL for later use

                self.get_vacancy_page()

            current_page += 1

        # Logging processes
        log_URLs(self.website_loker, self.temp_logged_URLs) # Log the URLs that have been processed to avoid re-scraping in the future
        if self.local_log:
            insert_rows(self.accepted_vacancies, db_type="accepted")
            insert_rows(self.all_vacancies, db_type="overall")

        return self.accepted_vacancies, self.all_vacancies
