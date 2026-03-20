import logging

from fastapi import FastAPI
from app.core.config import settings
from app.api.health import router as health_router
from app.api.db_test import router as db_test_router
from app.api.jobs import router as jobs_router
from app.api.job_parser import router as job_parser_router
from app.api.candidate_profiles import router as candidate_profiles_router
from app.api.candidate_profile_analysis import router as candidate_profile_analysis_router
from app.api.job_match import router as job_match_router
from app.api.cv_generator import router as cv_generator_router
from app.db.init_db import init_db
from app.api.cv_text import router as cv_text_router
from app.api.cover_letter import router as cover_letter_router
from app.api.cover_letter_text import router as cover_letter_text_router
from app.api.ats_score import router as ats_score_router
from app.api.ats_explanation import router as ats_explanation_router
from app.api.application_package import router as application_package_router
from app.api.application_package_text import router as application_package_text_router
from app.api.application_package_store import router as application_package_store_router
from app.api.applications import router as applications_router
from app.api.application_summary import router as application_summary_router
from app.api.job_ingestion import router as job_ingestion_router
from app.api.job_ingestion_package import router as job_ingestion_package_router
from app.api.scraper import router as scraper_router
from app.api.scraper_ingestion import router as scraper_ingestion_router
from app.api.scraper_package import router as scraper_package_router
from app.api.site_scraper import router as site_scraper_router
from app.api.site_scraper_debug import router as site_scraper_debug_router
from app.api.llm_job_parser import router as llm_job_parser_router
from app.api.llm_models import router as llm_models_router
from app.api.job_chat import router as job_chat_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health_router)
app.include_router(db_test_router)
app.include_router(jobs_router)
app.include_router(job_parser_router)
app.include_router(candidate_profiles_router)
app.include_router(candidate_profile_analysis_router)
app.include_router(job_match_router)
app.include_router(cv_generator_router)
app.include_router(cv_text_router)
app.include_router(job_chat_router)
app.include_router(cover_letter_router)
app.include_router(cover_letter_text_router)
app.include_router(ats_score_router)
app.include_router(ats_explanation_router)
app.include_router(application_package_router)
app.include_router(application_package_text_router)
app.include_router(application_package_store_router)
app.include_router(applications_router)
app.include_router(application_summary_router)
app.include_router(job_ingestion_router)
app.include_router(job_ingestion_package_router)
app.include_router(scraper_router)
app.include_router(scraper_ingestion_router)
app.include_router(scraper_package_router)
app.include_router(site_scraper_router)
app.include_router(site_scraper_debug_router)
app.include_router(llm_job_parser_router)
app.include_router(llm_models_router)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "environment": settings.APP_ENV
    }