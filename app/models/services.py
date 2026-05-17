"""
Pydantic models for service requests (repair/fixing services).

For junior developers:
- These models define the shape of service request/response data
- Used for automatic validation and API documentation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ServiceCreate(BaseModel):
    """Schema for creating a new service listing."""
    title: str
    description: str
    price: float
    service_type: str  # e.g., "screen_repair", "keyboard_repair", "battery_replacement", "software_install", "cleaning", "other"
    brand: Optional[str] = None
    turnaround_time: Optional[str] = None  # e.g., "Same day", "1-2 days", "3-5 days"
    warranty_days: Optional[int] = None


class ServiceUpdate(BaseModel):
    """Schema for updating a service listing."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    service_type: Optional[str] = None
    brand: Optional[str] = None
    turnaround_time: Optional[str] = None
    warranty_days: Optional[int] = None


class ServiceResponse(BaseModel):
    """Schema for service listing response."""
    id: str
    title: str
    description: str
    price: float
    service_type: str
    brand: Optional[str] = None
    turnaround_time: Optional[str] = None
    warranty_days: Optional[int] = None
    image_url: Optional[str] = None
    seller_id: str
    created_at: str
    updated_at: str
