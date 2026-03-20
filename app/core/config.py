from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Application Agent"
    APP_ENV: str = Field("dev", pattern="^(dev|staging|prod)$")

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DATABASE_URL: PostgresDsn = Field(
        "postgresql://postgres:postgres@localhost:5432/ai_job_agent",
        env="DATABASE_URL",
    )

    CORS_ORIGINS: Optional[str] = Field(None, env="CORS_ORIGINS")

    GEMINI_API_KEY: Optional[str] = Field(None, env="GEMINI_API_KEY")

    # By default this project uses the Gemini Developer API.
    # If you need to use Vertex AI (GCP), set GEMINI_USE_VERTEXAI to true and provide project/location.
    GEMINI_USE_VERTEXAI: bool = Field(False, env="GEMINI_USE_VERTEXAI")
    GEMINI_VERTEXAI_PROJECT: Optional[str] = Field(None, env="GEMINI_VERTEXAI_PROJECT")
    GEMINI_VERTEXAI_LOCATION: Optional[str] = Field(None, env="GEMINI_VERTEXAI_LOCATION")

    # The default model should be one that supports text generation via generateContent.
    # gemini-3-flash is not available for the current API version (v1beta), so we default to a supported model.
    GEMINI_MODEL: str = Field("gemini-1.0", env="GEMINI_MODEL")

    # Optional custom prompts for LLM usage
    LLM_JOB_PARSER_PROMPT: Optional[str] = Field(None, env="LLM_JOB_PARSER_PROMPT")
    LLM_CV_REWRITE_PROMPT: Optional[str] = Field(None, env="LLM_CV_REWRITE_PROMPT")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]



settings = Settings()