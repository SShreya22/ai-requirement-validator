import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_requirements(text: str):
    prompt = f"""
    Read the following text and extract:
    - Functional requirements (what the system should do).
    - Non-functional requirements (performance, security, usability).

    Text: "{text}"

    Format response as:
    Functional Requirements:
    1. ...
    2. ...
    
    Non-Functional Requirements:
    1. ...
    2. ...
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

def parse_requirements(ai_response: str):
    functional = []
    non_functional = []
    
    lines = ai_response.split("\n")
    category = None
    
    for line in lines:
        if "Functional Requirements" in line:
            category = "functional"
        elif "Non-Functional Requirements" in line:
            category = "non-functional"
        elif line.strip().startswith("-") or line.strip()[0].isdigit():
            if category == "functional":
                functional.append(line.strip("- "))
            elif category == "non-functional":
                non_functional.append(line.strip("- "))

    return {"Functional Requirements": functional, "Non-Functional Requirements": non_functional}
