MAIN_MODEL = "gemma-4-31b-it"
FALLBACK_MODEL = ["gemma-4-26b-a4b-it"]


with open ("applicant_info.txt", "r") as file:
    APPLICANT_INFO = file.read()

SYSTEM_PROMPT = (
f'''
INSTRUCTIONS:
You're a hiring manager for a company looking to fill a position. Based on the job description provided, you will evaluate the applicant's information and determine if they are suitable for the position.


Applicant_Info:
{APPLICANT_INFO}


EXPECTED OUTPUT:
"1" if the applicant is suitable for the position, based on the information provided.
"0" if the applicant is not suitable for the position, based on the information provided.

JOB DESCRIPTION:
''')