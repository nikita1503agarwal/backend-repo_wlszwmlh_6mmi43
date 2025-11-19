import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import (
    Photographer,
    ServicePackage,
    PortfolioItem,
    Testimonial,
    Booking,
    Enquiry,
    Client,
    Gallery,
    Announcement,
)

app = FastAPI(title="Pictiv.Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Pictiv.Studio backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# Basic listing endpoints for frontend consumption

@app.get("/api/portfolio", response_model=List[PortfolioItem])
def list_portfolio(category: Optional[str] = None, limit: int = 36):
    filt = {"category": category} if category else {}
    docs = get_documents("portfolioitem", filt, limit)
    # Convert ObjectId to str and coerce to PortfolioItem
    items: List[PortfolioItem] = []
    for d in docs:
        d.pop("_id", None)
        items.append(PortfolioItem(**d))
    return items


@app.get("/api/packages", response_model=List[ServicePackage])
def list_packages(category: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    filt = {}
    if category:
        filt["category"] = category
    if featured is not None:
        filt["featured"] = featured
    docs = get_documents("servicepackage", filt, limit)
    for d in docs:
        d.pop("_id", None)
    return [ServicePackage(**d) for d in docs]


@app.get("/api/testimonials", response_model=List[Testimonial])
def list_testimonials(limit: int = 20):
    docs = get_documents("testimonial", {}, limit)
    for d in docs:
        d.pop("_id", None)
    return [Testimonial(**d) for d in docs]


@app.get("/api/announcements", response_model=List[Announcement])
def list_announcements(limit: int = 10):
    docs = get_documents("announcement", {"active": True}, limit)
    for d in docs:
        d.pop("_id", None)
    return [Announcement(**d) for d in docs]


# Submission endpoints

@app.post("/api/enquire")
def create_enquiry(payload: Enquiry):
    _id = create_document("enquiry", payload)
    return {"status": "ok", "id": _id}


@app.post("/api/book")
def create_booking(payload: Booking):
    _id = create_document("booking", payload)
    return {"status": "ok", "id": _id}


# Simple client auth for gallery (code-based)
class LoginPayload(BaseModel):
    email: str
    access_code: str


@app.post("/api/client/login")
def client_login(payload: LoginPayload):
    # NOTE: In a full implementation we'd verify against the Client collection
    # For now, accept any non-empty and create a short-lived token-like echo
    if not payload.email or not payload.access_code:
        raise HTTPException(status_code=400, detail="Missing credentials")
    token = f"tok_{abs(hash(payload.email + payload.access_code))}"
    return {"token": token}


@app.get("/api/galleries", response_model=List[Gallery])
def list_galleries(email: Optional[str] = None, limit: int = 20):
    filt = {"client_email": email} if email else {}
    docs = get_documents("gallery", filt, limit)
    for d in docs:
        d.pop("_id", None)
    return [Gallery(**d) for d in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
