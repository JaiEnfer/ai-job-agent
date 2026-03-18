from pydantic import BaseModel


class ApplicationPackageStatusUpdate(BaseModel):
    status: str