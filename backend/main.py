import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
import fitz
from pptx import Presentation
from docx import Document
import pandas as pd

# Load API key securely
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI app setup
app = FastAPI()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Input data model for direct text input
class RequirementInput(BaseModel):
    text: str

# Home Route
@app.get("/")
async def home():
    return {"message": "Welcome to the Requirement Extraction API!"}

# File Upload and Extraction Route
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Extract text
    extracted_text = extract_text(file_path)
    
    if extracted_text == "Unsupported file format":
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Send extracted text to requirement extraction endpoint
    prompt = f"Extract and categorize the following text into Functional and Non-Functional requirements:\n{extracted_text}"

    try:
        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}]
)


        extracted_requirements = response["choices"][0]["message"]["content"]

        # Generate Word & Excel files
        word_file = generate_word_file(extracted_requirements)
        excel_file = generate_excel_file(extracted_requirements)

        return {
            "message": "Files generated successfully!",
            "word_file": word_file,
            "excel_file": excel_file,
            "requirements": extracted_requirements
        }

    except Exception as e:
        return {"error": str(e)}

# Text Extraction Logic
def extract_text(file_path):
    file_ext = file_path.split(".")[-1].lower()

    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found"

    if file_ext == "pdf":
        doc = fitz.open(file_path)
        text = "\n".join([page.get_text("text") for page in doc])

    elif file_ext in ["doc", "docx"]:
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    elif file_ext in ["xls", "xlsx"]:
        df = pd.read_excel(file_path)
        text = df.to_string()

    elif file_ext == "pptx":  # ✅ Added PPTX support
        try:
            prs = Presentation(file_path)
            text = "\n".join([
                shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")
            ])
        except Exception as e:
            return f"Error extracting text from PPTX: {str(e)}"

    else:
        return "Unsupported file format"

    return text

# Requirement Extraction Endpoint (For Direct Text)
@app.post("/extract-requirements/")
async def extract_requirements(input_data: RequirementInput):
    prompt = f"Extract and categorize the following text into Functional and Non-Functional requirements:\n{input_data.text}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Analyze the uploaded document."},
            ]
        )


        extracted_requirements = response["choices"][0]["message"]["content"]

        # Generate Word & Excel files
        word_file = generate_word_file(extracted_requirements)
        excel_file = generate_excel_file(extracted_requirements)

        return {
            "message": "Files generated successfully!",
            "word_file": word_file,
            "excel_file": excel_file,
            "requirements": extracted_requirements
        }

    except Exception as e:
        return {"error": str(e)}

# Function to generate Word document
def generate_word_file(requirements):
    doc = Document()
    doc.add_heading("Extracted Requirements", level=1)
    doc.add_paragraph(requirements)
    file_path = "requirements.docx"
    doc.save(file_path)
    return file_path

# Function to generate Excel file
def generate_excel_file(requirements):
    df = pd.DataFrame({"Requirements": [requirements]})
    file_path = "user_stories.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

# File Download Routes
@app.get("/download-word/")
async def download_word():
    return FileResponse("requirements.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="requirements.docx")

@app.get("/download-excel/")
async def download_excel():
    return FileResponse("user_stories.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="user_stories.xlsx")
