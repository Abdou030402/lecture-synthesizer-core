import os
from PyPDF2 import PdfReader

def is_text_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return any(page.extract_text() for page in reader.pages)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    all_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            all_text += page_text + "\n"
    return all_text.strip()

def analyze_and_save(pdf_path):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_folder = os.path.join(root_dir, "OCR_outputs/printed_text_output")
    os.makedirs(output_folder, exist_ok=True)

    pdf_filename = os.path.basename(pdf_path)
    output_filename = os.path.splitext(pdf_filename)[0] + ".txt"
    output_path = os.path.join(output_folder, output_filename)

    extracted_text = ""

    if is_text_pdf(pdf_path):
        extracted_text = extract_text_from_pdf(pdf_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"✅ Text extracted and saved to: {output_path}")
    else:
        print("⚠️ This PDF does not contain extractable text. Use OCR instead.")
    
    return extracted_text


if __name__ == "__main__":  
    analyze_and_save("OCR_test_documents/test_printed.pdf")
