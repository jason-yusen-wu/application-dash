from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/applications", tags=["applications"])


class Application(BaseModel):
    id: int
    company: str
    role: str
    status: str


# Placeholder in-memory data so the dashboard has something to render.
# Replace with real queries once your database schema exists.
_MOCK_APPLICATIONS = [
    Application(id=1, company="Acme Corp", role="Backend Engineer", status="Applied"),
    Application(id=2, company="Globex", role="Data Scientist", status="Interviewing"),
    Application(id=3, company="Initech", role="SRE", status="Offer"),
]


@router.get("", response_model=list[Application])
def list_applications():
    return _MOCK_APPLICATIONS


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{application_id}", response_model=Application)
def update_status(application_id: int, update: StatusUpdate):
    for application in _MOCK_APPLICATIONS:
        if application.id == application_id:
            application.status = update.status
            return application
    raise HTTPException(status_code=404, detail="Application not found")
