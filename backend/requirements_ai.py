import os
from dotenv import load_dotenv
import requests

load_dotenv()  # Load API key from .env file

# You will use Gemini API here, so replace OpenAI key with Gemini key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Load the Gemini API key

def get_gemini_response(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    # Send the POST request to the Gemini API
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the response content from Gemini
    else:
        return {"error": f"API Error: {response.status_code}", "message": response.text}

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

    response = get_gemini_response(prompt)
    
    # Assuming the response will contain the extracted requirements
    if "choices" in response:
        return response["choices"][0]["message"]["content"]
    else:
        return {"error": "Failed to extract requirements", "details": response}

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
