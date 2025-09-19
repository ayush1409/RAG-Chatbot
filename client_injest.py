import requests
import PyPDF2
import uuid

def extract_text_from_pdf(pdf_path):
    text_content = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
    return text_content.strip()

def prepare_body(pdf_paths):
    docs = []
    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(pdf_path)
        doc = {
            "id": str(uuid.uuid4()),
            "title": pdf_path.split("/")[-1],
            "text": text
        }
        docs.append(doc)
    return {"docs": docs}

def send_docs_to_api(api_url, pdf_paths):
    body = prepare_body(pdf_paths)
    print(body)
    response = requests.post(api_url, json=body)
    if response.status_code == 201 or response.status_code == 200:
        print("✅ Successfully sent data")
        print(response.json())
    else:
        print(f"❌ Error: {response.tatus_code}, {response.text}")

if __name__ == "__main__":
    API_URL = "http://127.0.0.1:8000/ingest" 
    PDF_FILES = ["./cricket_info.pdf"]
    
    send_docs_to_api(API_URL, PDF_FILES)
