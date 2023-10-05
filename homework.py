import openai
import os
import sys
import pytesseract
from PIL import Image
from pdf2image import convert_from_path, pdf2image
from docx import Document
Image.MAX_IMAGE_PIXELS = None

print("working on it")

api_key = "CHANGE THIS"
openai.api_key = api_key

def perform_ocr(image):
    return pytesseract.image_to_string(image)

def extract_text_from_single_page(args):
    pdf_path, page_num = args
    image = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)[0]
    return perform_ocr(image) + "\n"

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    total_pages = pdf2image.pdfinfo_from_path(pdf_path)['Pages']
    page_texts = [extract_text_from_single_page((pdf_path, page_num)) for page_num in range(total_pages)]
    extracted_text += "".join(page_texts)
    return extracted_text



def save_to_txt(input_text, output_directory, output_filename):
    output_file_path = os.path.join(output_directory, output_filename)
    with open(output_file_path, 'w') as file:
        file.write(input_text)
    return output_file_path

def save_to_docx(input_text, output_directory, output_filename):
    doc = Document()
    doc.add_paragraph(input_text)
    output_file_path = os.path.join(output_directory, output_filename)
    doc.save(output_file_path)
    return output_file_path

try:
    pdf_path = sys.argv[1]
    pdf_directory = os.path.dirname(pdf_path)
except IndexError:
    print("Please provide the path to a PDF file.")
    sys.exit(1)

extracted_text = extract_text_from_pdf(pdf_path)
chunk_size = 3500
chunks = [extracted_text[i:i+chunk_size] for i in range(0, len(extracted_text), chunk_size)]
complete_response = ""

for chunk in chunks:
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Can you make 1 paragraphs of notes from this " + chunk}])
    response = completion['choices'][0]['message']['content']
    complete_response += '\n'+ '\n' + response

# Save as TXT
txt_output_filename = "notes.txt"
txt_output_path = save_to_txt(complete_response, pdf_directory, txt_output_filename)
print("Notes saved to", txt_output_path)

# Save as DOCX
docx_output_filename = "notes.docx"
docx_output_path = save_to_docx(complete_response, pdf_directory, docx_output_filename)
print("Notes saved to", docx_output_path)
