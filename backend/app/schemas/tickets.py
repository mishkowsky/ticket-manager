from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.database import StatusEnum, PriorityEnum


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    priority: PriorityEnum = PriorityEnum.normal


class TicketUpdate(BaseModel):
    status: StatusEnum


class TicketResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    priority: PriorityEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
