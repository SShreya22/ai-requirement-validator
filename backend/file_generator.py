from requirements_ai import extract_requirements, parse_requirements
from file_generator import generate_word_file, generate_excel_file

# Example usage:
text_to_extract = "Your long PDF or text content goes here..."
extracted_text = extract_requirements(text_to_extract)

# If extraction is successful, parse and generate files
if "error" not in extracted_text:
    parsed_requirements = parse_requirements(extracted_text)
    generate_word_file(parsed_requirements)
    generate_excel_file(parsed_requirements)
else:
    print("Error:", extracted_text["error"])
