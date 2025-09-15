"""
Simple RAG API using FastAPI + LangChain + Chroma (default) + OpenAI chat + OpenAI embeddings.

Endpoints:
- POST /ingest  -> ingest documents (list of {id,title,text})
- POST /query   -> ask a question -> returns {answer, sources}
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, HTTPException
from chain.build_chain import _build_chain
from schema import IngestRequest, QueryRequest, QueryResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from utils import CHROMA_DB_DIR, OPENAI_API_KEY, VECTOR_BACKEND


# Setup LangChain components (embeddings, llm, vectorstore)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

if VECTOR_BACKEND == "chroma":
    vector_store = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
else:
    raise RuntimeError(f"Unsupported VECTOR_BACKEND: {VECTOR_BACKEND}")

# Create directory for Vector DB if not exists
@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    yield

app = FastAPI(title="RAG Chatbot", lifespan=lifespan)


# ---- Ingest endpoint: split docs -> create Document objects with metadata -> add to vector store ----
@app.post("/ingest", status_code=201)
def ingest(req: IngestRequest):
    """
    Ingest a list of documents. Each doc will be chunked (overlapping chunks),
    each chunk will be embedded and stored with metadata:
      metadata = {"source_id": doc.id, "title": doc.title, "chunk_index": i}
    """
    docs_to_add = []
    for doc in req.docs:
        chunks = text_splitter.split_text(doc.text)
        for i, chunk in enumerate(chunks):
            metadata = {"source_id": doc.id, "title": doc.title or "", "chunk_index": i}
            docs_to_add.append(Document(page_content=chunk, metadata=metadata))

    if not docs_to_add:
        raise HTTPException(status_code=400, detail="No document text to ingest")

    vector_store.add_documents(docs_to_add)
    if VECTOR_BACKEND == "chroma":
        vector_store.persist()
    return {"ingested_chunks": len(docs_to_add)}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Query the corpus:
     - Retrieve top_k chunks
     - Run the LLM with the retrieved context
     - Return the answer and the source metadata for provenance
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    chain = _build_chain(llm, top_k=req.top_k, vector_store=vector_store)

    # We use the generic API that returns {'result'|'answer' ... , 'source_documents': [...] }
    result = chain.invoke({"input": req.query})

    if isinstance(result, str):
        answer = result
        source_docs = []
    elif isinstance(result, dict):
        answer = result.get("result") or result.get("output_text") or result.get("answer") or str(result)
        source_docs = result.get("source_documents") or result.get("source_documents", [])
    else:
        answer = str(result)
        source_docs = []

    sources = []
    for sd in source_docs:
        md = getattr(sd, "metadata", None) or sd.get("metadata", {})
        sources.append({
            "source_id": md.get("source_id"),
            "title": md.get("title"),
            "chunk_index": md.get("chunk_index"),
            "score": getattr(sd, "score", None) or md.get("score")
        })

    return QueryResponse(answer=answer, sources=sources)