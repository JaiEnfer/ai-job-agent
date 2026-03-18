from app.db.session import engine, Base
import app.models  # important: ensures models are imported


def init_db():
    Base.metadata.create_all(bind=engine)