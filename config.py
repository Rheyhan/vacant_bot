import datetime

# GEMINI CONFIGURATION FILE
MAIN_MODEL = "gemma-4-31b-it"
FALLBACK_MODEL = ["gemma-4-26b-a4b-it"]

with open ("applicant_info.txt", "r") as file:
    APPLICANT_INFO = file.read()

SYSTEM_PROMPT = (
f'''
INSTRUCTIONS:
You are a strict hiring manager looking for a candidate to fill a position. Based on the JOB DESCRIPTION provided at the end, you will evaluate the applicant's information, compare it against the job requirements, and determine if they are highly suitable to be called for an interview.

Applicant_Info:
{APPLICANT_INFO}

Instructions for Output:
First, provide a brief 2-3 sentence reasoning analyzing the match between the applicant's skills and the job description.
Then, output exactly in the following JSON format without any markdown code blocks:
{{"acceptance": "1 or 0", "Position": ["Name of all suitable position(s) from the job description"], "Reason": "Brief explanation of the decision."}}

JOB DESCRIPTION:
''')

# A dictionary containing the websites to scrape and their corresponding base URLs
WEB_DICT = {
    "Disnakerja": "https://www.disnakerja.com/page/",
    "Inginkerja": "https://inginkerja.id/page/",
    "RekrutmenBersama": "https://rekrutmenbersama.co.id/page/"
    }

# CONSTANTS FOR WAIT TIMES AND DATE CALCULATIONS
SHORT_WAIT = 2  # used for short delays
LONG_WAIT = 8  # used for long delays
API_TIMEOUT = 30 # used for API calls timeout
MAX_PAST_DAYS = 14  # maximum number of days to consider a job posting as recent

# Database paths and table names
ACCEPTED_DB_PATH = "SQL_DATA/Accepted_vacancies.db"
TABLE_NAME_ACCEPTED_DB = "Accepted_vacancies"
OVERALL_DB_PATH = "SQL_DATA/All_logged_vacancies.db"
TABLE_NAME_OVERALL_DB = "All_vacancies"

CHROME_EXECUTABLE_PATH = "D:/chrome-win64/chrome.exe"
DRIVER_EXECUTABLE_PATH = "D:/chromedriver-win64/chromedriver.exe"

CURRENT_DATE = datetime.datetime.now().date()
MAX_PAST_DATE = CURRENT_DATE - datetime.timedelta(days=MAX_PAST_DAYS)