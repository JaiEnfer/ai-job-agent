from pydantic import BaseModel


class JobChatResponse(BaseModel):
    job_text: str
    answer: str
