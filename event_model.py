from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class EventItem(BaseModel):
    title: Optional[str] = Field(None, description="Event title")
    url: Optional[HttpUrl] = Field(None, description="Event source URL")
    start_date: Optional[datetime] = Field(None, description="Start date and time")
    timezone: Optional[str] = Field(None, description="Timezone")
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    venue: Optional[str] = Field(None, description="Venue name")
    segment: Optional[str] = Field(None, description="Segment")
    genre: Optional[str] = Field(None, description="Genre")
    subgenre: Optional[str] = Field(None, description="Subgenre")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    image_url: Optional[HttpUrl] = Field(None, description="Image URL")
    sales_start: Optional[datetime] = Field(None, description="Sales start")
    sales_end: Optional[datetime] = Field(None, description="Sales end")
    promoter: Optional[str] = Field(None, description="Promoter")