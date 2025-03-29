from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from requirements_ai import extract_requirements, parse_requirements
from file_generator import generate_word_file, generate_excel_file

app = FastAPI()

@app.post("/process-text/")
async def process_text(text: str = Form(...)):
    ai_output = extract_requirements(text)
    structured_reqs = parse_requirements(ai_output)

    word_file = generate_word_file(structured_reqs)
    excel_file = generate_excel_file(structured_reqs)

    return {
        "message": "Files generated successfully!",
        "word_file": word_file,
        "excel_file": excel_file,
        "ai_response": ai_output
    }

@app.get("/download-word/")
async def download_word():
    return FileResponse("requirements.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="requirements.docx")

@app.get("/download-excel/")
async def download_excel():
    return FileResponse("user_stories.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="user_stories.xlsx")
