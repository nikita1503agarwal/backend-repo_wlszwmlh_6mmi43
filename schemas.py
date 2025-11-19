"""
Database Schemas for Pictiv.Studio

Each Pydantic model corresponds to a MongoDB collection. The collection
name is the lowercase of the class name (e.g., ServicePackage -> "servicepackage").

These schemas are used for validation in API endpoints and for the database viewer.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class Photographer(BaseModel):
    name: str
    location: str = Field(..., description="City/region, e.g., Nashik")
    bio: str
    instagram: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class ServicePackage(BaseModel):
    title: str
    category: str = Field(..., description="wedding | prewedding | maternity | portrait | event | custom")
    description: Optional[str] = None
    deliverables: List[str] = Field(default_factory=list)
    duration_hours: Optional[float] = None
    price: Optional[float] = Field(None, ge=0)
    addons: List[str] = Field(default_factory=list)
    featured: bool = False


class PortfolioItem(BaseModel):
    title: str
    category: str = Field(..., description="wedding | portrait | maternity | other")
    image_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    highlight: bool = False


class Testimonial(BaseModel):
    client_name: str
    content: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    date: Optional[datetime] = None


class Booking(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    preferred_date: str
    preferred_time: Optional[str] = None
    location: Optional[str] = None
    package_id: Optional[str] = None
    notes: Optional[str] = None
    status: str = Field("pending", description="pending | confirmed | cancelled | completed")


class Enquiry(BaseModel):
    name: str
    contact: str
    category: Optional[str] = None
    message: Optional[str] = None


class Client(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    access_code: str = Field(..., min_length=4)
    session_token: Optional[str] = None
    session_expires_at: Optional[datetime] = None


class Gallery(BaseModel):
    client_email: EmailStr
    title: str
    images: List[str] = Field(default_factory=list)
    allow_download: bool = True
    watermarked: bool = True


class Announcement(BaseModel):
    title: str
    content: str
    active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
