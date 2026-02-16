from datetime import datetime
from typing import Optional
from ninja import Schema
from typing import Optional
from typing import List


class LocationOut(Schema):
    id: int
    name: str
    category: str
    address: Optional[str] = None
    website: Optional[str] = None
    country_code: str
    related_store_external_id: str

    lat: Optional[float] = None
    lng: Optional[float] = None


class EventOut(Schema):
    id: int
    title: str
    sub_title_thai: Optional[str] = None
    description: str
    description_thai: Optional[str] = None
    banner_image: str
    event_type: str

    start_date: datetime
    end_date: Optional[datetime] = None

    location_id: int
    location_name: str
    location_category: str
    location_address: Optional[str] = None
    location_website: Optional[str] = None
    country_code: str

    lat: Optional[float] = None
    lng: Optional[float] = None

    # only set by /events/nearby
    distance_km: Optional[float] = None

    @staticmethod
    def resolve_location_address(obj):
        return obj.location.address if obj.location else None
    @staticmethod
    def resolve_location_website(obj):
        return obj.location.website if obj.location else None


class MemberProfileOut(Schema):
    id: int
    user_id: int
    home_city: str
    interests: List[str]
    saved_event_ids: List[int]


