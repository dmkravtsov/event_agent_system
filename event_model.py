from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class EventItem(BaseModel):
    source_id: Optional[str] = Field(None, description="Internal source event ID")
    title: Optional[str] = Field(None, description="Event title")
    url: Optional[HttpUrl] = Field(None, description="Event source URL")

    start_date: Optional[datetime] = Field(None, description="Start date and time")
    sales_start: Optional[datetime] = Field(None, description="Sales start")
    sales_end: Optional[datetime] = Field(None, description="Sales end")
    duration_seconds: Optional[int] = Field(None, description="Event duration in seconds")
    timezone: Optional[str] = Field(None, description="Timezone")

    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    venue: Optional[str] = Field(None, description="Venue name")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")

    segment: Optional[str] = Field(None, description="Segment")
    genre: Optional[str] = Field(None, description="Genre")
    subgenre: Optional[str] = Field(None, description="Subgenre")
    category: Optional[str] = Field(None, description="Event category")
    labels: Optional[List[str]] = Field(None, description="Event labels")

    promoter: Optional[str] = Field(None, description="Promoter")

    attendance: Optional[int] = Field(None, description="Estimated attendance")
    predicted_spend: Optional[float] = Field(None, description="Predicted spend at event")

    description: Optional[str] = Field(None, description="Event description")
    image_urls: Optional[List[HttpUrl]] = Field(None, description="List of image URLs")
    ticket_urls: Optional[List[HttpUrl]] = Field(None, description="List of ticket purchase links")

    price: Optional[float] = Field(None, description="Ticket price, if known")

# class EventItem(BaseModel):
#     title: Optional[str] = Field(None, description="Event title")
#     url: Optional[HttpUrl] = Field(None, description="Event source URL")
#     start_date: Optional[datetime] = Field(None, description="Start date and time")
#     timezone: Optional[str] = Field(None, description="Timezone")
#     city: Optional[str] = Field(None, description="City")
#     country: Optional[str] = Field(None, description="Country")
#     venue: Optional[str] = Field(None, description="Venue name")
#     segment: Optional[str] = Field(None, description="Segment")
#     genre: Optional[str] = Field(None, description="Genre")
#     subgenre: Optional[str] = Field(None, description="Subgenre")
#     latitude: Optional[float] = Field(None, description="Latitude")
#     longitude: Optional[float] = Field(None, description="Longitude")
#     image_url: Optional[HttpUrl] = Field(None, description="Image URL")
#     sales_start: Optional[datetime] = Field(None, description="Sales start")
#     sales_end: Optional[datetime] = Field(None, description="Sales end")
#     promoter: Optional[str] = Field(None, description="Promoter")