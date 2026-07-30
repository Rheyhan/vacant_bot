from typing import Literal
import json
import os
import numpy as np

def log_URLs(web_type : Literal["Disnakerja", "Inginkerja", "RekrutmenBersama"], url : list[str]) -> None:
    '''
    Log the URLs that have been processed to avoid re-scraping in the future

    Parameters
    ----------
    - web_type : Literal["Disnakerja", "Inginkerja", "RekrutmenBersama"]
        The type of job website to log the URLs for
    - url : list[str]
        A list of URLs to be logged
    '''

    # Open the current logged_URL.json file and load its content
    with open("logged_URL.json", "r") as f:
        logged_URLs = json.load(f)

    # Get the latest logged URL index and then add the new URLs to the JSON structure
    latest_index = np.max([int(key) for key in logged_URLs[web_type].keys()]) if logged_URLs[web_type] else 1
    
    for i, link in enumerate(url[::-1]):  # Reverse the list to log from the bottom
        logged_URLs[web_type][str(latest_index + i)] = link

    # save the updated JSON structure back to the file
    with open("logged_URL.json", "w") as f:
        json.dump(logged_URLs, f, indent=4)


def get_past_URLs(web_type: Literal["Disnakerja", "Inginkerja", "RekrutmenBersama"] = None) -> str:
    '''
    Get the latest logged URL for each job website from the logged_URL.json file.
    '''

    # Check if logged_URL.json exists, if not create it and return None
    if not os.path.exists("logged_URL.json"):
        json_structure = {
            "Disnakerja": {
            },
            "Inginkerja": {
            },
            "RekrutmenBersama": {
            }
        }
        with open("logged_URL.json", "w") as f:
            json.dump(json_structure, f)
        return None

    # if it does exist, load the latest logged URL of the specified job website
    else:
        with open("logged_URL.json", "r") as f:
            logged_URLs = json.load(f)
        # Get the latest logged URL for each job website
        latest_url = logged_URLs[web_type].get(str(np.max([int(key) for key in logged_URLs[web_type].keys()]))) if logged_URLs[web_type] else None
        
        return latest_url