from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import Location, Event, MemberProfile
from .schemas import LocationOut, EventOut, MemberProfileOut

router = Router(tags=["society"])

@router.get("/health")
def health(request):
    return {"ok": True, "service": "society"}


def _loc_lat(loc: Location) -> Optional[float]:
    if not loc.coordinates:
        return None
    return float(loc.coordinates.y)


def _loc_lng(loc: Location) -> Optional[float]:
    if not loc.coordinates:
        return None
    return float(loc.coordinates.x)


def location_to_out(loc: Location) -> LocationOut:
    return LocationOut(
        id=loc.id,
        name=loc.name,
        category=loc.category,
        address=loc.address or "",
        website=loc.website,
        country_code=loc.country_code,
        related_store_external_id=loc.related_store_external_id or "",
        lat=_loc_lat(loc),
        lng=_loc_lng(loc),
    )


def event_to_out(e: Event, distance_km: Optional[float] = None) -> EventOut:
    loc = e.location
    return EventOut(
        id=e.id,
        title=e.title,
        description=e.description or "",
        banner_image=e.banner_image or "",
        event_type=e.event_type,
        start_date=e.start_date,
        end_date=e.end_date,
        location_id=loc.id,
        location_name=loc.name,
        location_category=loc.category,
        country_code=loc.country_code,
        lat=_loc_lat(loc),
        lng=_loc_lng(loc),
        distance_km=distance_km,
    )


@router.get("/locations", response=List[LocationOut])
def list_locations(
    request,
    country_code: Optional[str] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
):
    qs = Location.objects.all().order_by("country_code", "name")

    if country_code:
        qs = qs.filter(country_code__iexact=country_code)

    if category:
        qs = qs.filter(category=category)

    if q:
        qs = qs.filter(name__icontains=q)

    return qs


@router.get("/events", response=List[EventOut])
def list_events(
    request,
    country_code: Optional[str] = None,
    event_type: Optional[str] = None,
    location_id: Optional[int] = None,
    upcoming_only: bool = True,
):
    qs = Event.objects.select_related("location").order_by("-start_date")

    if country_code:
        qs = qs.filter(location__country_code__iexact=country_code)

    if event_type:
        qs = qs.filter(event_type=event_type)

    if location_id:
        qs = qs.filter(location_id=location_id)

    if upcoming_only:
        # Upcoming events ordered by soonest
        qs = qs.order_by("start_date")
    else:
        qs = qs.order_by("-start_date")

    return qs


@router.get("/events/nearby", response=List[EventOut])
def events_nearby(
    request,
    lat: float,
    lng: float,
    km: float = 25.0,
    event_type: Optional[str] = None,
    upcoming_only: bool = True,
):
    """
    Finds events near a lat/lng within radius km.
    Works great because Location.coordinates uses geography=True.
    """
    user_point = Point(lng, lat, srid=4326)

    qs = (
        Event.objects.select_related("location")
        .filter(location__coordinates__isnull=False)
        .annotate(distance=Distance("location__coordinates", user_point))
        .filter(location__coordinates__distance_lte=(user_point, D(km=km)))
    )

    if event_type:
        qs = qs.filter(event_type=event_type)

    if upcoming_only:
        qs = qs.order_by("start_date", "distance")
    else:
        qs = qs.order_by("distance", "-start_date")

    out: List[EventOut] = []
    for e in qs:
        dist = getattr(e, "distance", None)

        # With geography=True, dist usually supports .m (meters)
        distance_km = (dist.m / 1000.0) if dist is not None and hasattr(dist, "m") else None
        out.append(event_to_out(e, distance_km=distance_km))

    return out

@router.get("/member_profiles/{profile_id}", response=MemberProfileOut)
def get_member_profile(
    request, profile_id: int):
    profile = get_object_or_404(MemberProfile, id=profile_id)

    return MemberProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        home_city=profile.home_city,
        interests=profile.interests,
        saved_event_ids=list(profile.saved_events.values_list("id", flat=True)),
    )



    
