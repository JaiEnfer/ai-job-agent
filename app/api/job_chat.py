from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session

from app.schemas.job_chat import JobChatResponse
from app.services.resume_parser import extract_text_from_resume
from app.services.llm_text import generate_text

router = APIRouter(prefix="/job-chat", tags=["job-chat"])


@router.post("", response_model=JobChatResponse)
async def job_chat(
    job_file: UploadFile = File(...),
    question: str = Form(...),
):
    """Accept a job description file and a question, then answer using the LLM."""

    text = extract_text_from_resume(job_file)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract text from the uploaded job file.")

    prompt = (
        "You are a friendly job analyst. Use the job description below to answer the user question. "
        "Be concise, focus on the job description, and use bullet points when appropriate.\n\n"
        "Job Description:\n" + text + "\n\n"
        "User Question:\n" + question + "\n\n"
        "Answer:"  
    )

    answer = generate_text(prompt)
    return {
        "job_text": text,
        "answer": answer,
    }
