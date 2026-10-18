"""Entry point. Wires the steps together and serves the frontend.

    upload -> pdf_loader -> pdf_reader -> text_chunker -> retriever
    ask    -> retriever + qa_service (LLM) -> qa_logger
"""
import threading
import webbrowser

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import llm_client
import qa_logger
from config import CSV_LOG_PATH, FRONTEND_DIR, HOST, PORT
from pdf_loader import PDFLoadError, save_pdf
from pdf_reader import PDFReadError, read_pdf
from qa_service import answer_question
from retriever import Retriever
from text_chunker import chunk_pages

app = FastAPI(title="PDF Q&A")

# The app keeps one active document in memory.
state: dict = {"version": None, "filename": None, "retriever": None}


class Question(BaseModel):
    question: str


@app.get("/api/status")
def status():
    return {**llm_client.get_status(), "document": state["filename"]}


@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    try:
        version, path = save_pdf(file.file.read(), file.filename)
    except PDFLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        pages = read_pdf(path)
    except PDFReadError as exc:
        path.unlink(missing_ok=True)  # do not keep unusable files in the logs
        raise HTTPException(status_code=400, detail=str(exc))

    chunks = chunk_pages(pages)
    retriever = Retriever(chunks)

    state.update(version=version, filename=file.filename, retriever=retriever)
    return {"version": version, "filename": file.filename, "pages": len(pages),
            "chunks": len(chunks), "search_mode": retriever.mode}


@app.post("/api/ask")
def ask(body: Question):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please type a question.")
    if state["retriever"] is None:
        raise HTTPException(status_code=400, detail="Upload a PDF first.")
    try:
        result = answer_question(state["retriever"], question)
    except llm_client.LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    qa_logger.log_qa(state["version"], question, result["answer"], result["pages"])
    return result


@app.get("/api/log")
def download_log():
    if not CSV_LOG_PATH.exists():
        raise HTTPException(status_code=404, detail="No questions have been logged yet.")
    return FileResponse(CSV_LOG_PATH, media_type="text/csv", filename="qa_log.csv")


# Must stay last: serves the frontend folder at "/".
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    uvicorn.run(app, host=HOST, port=PORT)
