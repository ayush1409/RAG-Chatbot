import streamlit as st
import requests
import uuid
import PyPDF2
import fitz

# Replace with your actual FastAPI base URL
API_BASE_URL = "http://localhost:8000"

st.title("Document Ingestion and Q&A")

# Section 1: Upload documents and call /ingest
st.header("Input Documents")

uploaded_files = st.file_uploader(
    "Upload one or more documents (txt, pdf)", type=["txt", "pdf"], accept_multiple_files=True
)
def extract_text_from_pdf(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

if uploaded_files:
    if st.button("Upload Documents"):
        with st.spinner("Uploading and ingesting documents..."):
            docs = []
            for file in uploaded_files:
                try:
                    if file.type == "application/pdf":
                        # Read PDF bytes and extract text
                        file_bytes = file.read()
                        content = extract_text_from_pdf(file_bytes)
                    else:
                        # Assume text file
                        content = file.getvalue().decode("utf-8")
                except Exception as e:
                    st.error(f"Error processing file {file.name}: {e}")
                    continue
                doc = {
                    "id": str(uuid.uuid4()),
                    "title": file.name,
                    "text": content,
                }
                docs.append(doc)
            if docs:
                payload = {"docs": docs}
                try:
                    print(payload)
                    response = requests.post(f"{API_BASE_URL}/ingest", json=payload)
                    response.raise_for_status()
                    st.success("Documents ingested successfully!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to ingest documents: {e}")

st.markdown("---")

# Section 2: Ask a question and call /query
st.header("Ask a Question")

question = st.text_input("Enter your question:")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question before asking.")
    else:
        with st.spinner("Getting answer..."):
            try:
                # Assuming the /query endpoint expects JSON with {"question": "..."}
                response = requests.post(f"{API_BASE_URL}/query", json={"query": question})
                response.raise_for_status()
                data = response.json()
                # Display the response JSON nicely
                st.subheader("Answer:")
                st.json(data)
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to get answer: {e}")


