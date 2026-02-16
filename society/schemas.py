from datetime import datetime
from typing import Optional
from ninja import Schema
from typing import List


class LocationOut(Schema):
    id: int
    name: str
    category: str
    address: str | None = None
    website: str | None = None
    country_code: str
    related_store_external_id: str

    lat: Optional[float] = None
    lng: Optional[float] = None


class EventOut(Schema):
    id: int
    title: str
    sub_title_thai: str | None = None
    description: str
    description_thai: str | None = None
    banner_image: str
    event_type: str

    start_date: datetime
    end_date: Optional[datetime] = None

    location_id: int
    location_name: str
    location_category: str
    location_address: str
    location_website: str
    country_code: str

    lat: Optional[float] = None
    lng: Optional[float] = None

    # only set by /events/nearby
    distance_km: Optional[float] = None


class MemberProfileOut(Schema):
    id: int
    user_id: int
    home_city: str
    interests: List[str]
    saved_event_ids: List[int]
