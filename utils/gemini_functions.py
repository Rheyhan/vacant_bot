from config import MAIN_MODEL, FALLBACK_MODEL, SYSTEM_PROMPT
import pydantic
from google.genai import types
import re
import json


# Expected Gemini response format
class gemini_response_format(pydantic.BaseModel):
    acceptance: str
    position: list[str]
    reason: str

def verify_vacancy(GENAI_CLIENT, input_text: str) -> tuple:
    '''
    This function takes an input text (applicant information) and sends it to the Gemini API for evaluation against the job description.

    Parameters
    ----------
    GENAI_CLIENT : google.genai.GenerativeAI
        An instance of the Gemini API client used to send requests.

    input_text : str
        The applicant's information to be evaluated.

    Returns
    ----------
    tuple
        A tuple containing the Gemini API response and a status code (1 for success, 0 for failure).
    '''

    status = None
    gemini_response = None

    # Use main model, if it fails, fallback to the secondary model
    for model in [MAIN_MODEL] + [FALLBACK_MODEL]:
        try:
            gemini_response = GENAI_CLIENT.models.generate_content(
                model=model,
                contents=[SYSTEM_PROMPT, input_text],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=gemini_response_format,
                ))
            status = 1
            break
        except Exception as exc:
            status = 0

    return gemini_response, status

# Parse the Gemini API response
def parse_json_response(response_text: str) -> dict:
    '''
    This function takes a JSON response text from the Gemini API and parses it into a dictionary.

    Parameters
    ----------
    response_text : str
        The JSON response text from the Gemini API.

    Returns
    ----------
    dict
        A dictionary containing the parsed response.
    '''
    response_text = response_text.text.strip()

    try:
        # Normal json load
        response_dict = json.loads(response_text)
    except json.JSONDecodeError:
        # If method above doesn't work.
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try:
                response_dict = json.loads(match.group(0))
            except Exception as exc:
                response_dict = {}
        else:
            response_dict = {}

    # Now safely get your values (using .get() prevents KeyError if the schema fails)
    acceptance = response_dict.get("acceptance", "0")
    position = response_dict.get("position", [])
    reason = response_dict.get("reason", "No reason provided.")

    return acceptance, position, reason