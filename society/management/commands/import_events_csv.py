import csv
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from society.models import Event, Location


def norm(s: str) -> str:
    return (s or "").strip()


# Your CSV uses "Religious Ceremony" etc.
EVENT_TYPE_MAP = {
    "religious ceremony": Event.EventType.RELIGIOUS,
    "concert/entertainment": Event.EventType.CONCERT,
    "market/food festival": Event.EventType.MARKET,
    "community gathering": Event.EventType.COMMUNITY,

    # small extras (optional, just in case)
    "religious": Event.EventType.RELIGIOUS,
    "concert": Event.EventType.CONCERT,
    "market": Event.EventType.MARKET,
    "community": Event.EventType.COMMUNITY,
}


def normalize_url(url: str) -> str:
    url = norm(url)
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def parse_dt_flexible(value: str):
    """
    Supports:
    - ISO: 2026-03-01T10:00:00Z
    - DD/MM/YYYY: 01/03/2026
    - DD-MM-YYYY: 28-06-2026
    """
    value = norm(value)
    if not value:
        return None

    # Try ISO
    dt = parse_datetime(value)
    if dt:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt

    # Try date formats (assume midnight local tz)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(value, fmt)
            return timezone.make_aware(d) if timezone.is_naive(d) else d
        except ValueError:
            pass

    raise ValueError(f"Invalid datetime/date: {value}")


def resolve_location(row: dict) -> Location:
    """
    Accept either:
    - location_external_id (best, future-proof), or
    - location (temple name) (your current CSV)
    """
    loc_ext = norm(row.get("location_external_id"))
    if loc_ext:
        return Location.objects.get(related_store_external_id=loc_ext)

    loc_name = norm(row.get("location"))
    if not loc_name:
        raise ValueError("Missing location (or location_external_id)")

    # First: exact match
    qs = Location.objects.filter(name__iexact=loc_name)
    if qs.count() == 1:
        return qs.first()

    # Second: try contains (helps if CSV adds city like "(Cheshire)")
    qs = Location.objects.filter(name__icontains=loc_name.split("(")[0].strip())
    if qs.count() == 1:
        return qs.first()

    if qs.count() == 0:
        raise ValueError(f"Location not found by name: '{loc_name}'. Add location_external_id column for reliability.")
    raise ValueError(f"Multiple locations matched '{loc_name}'. Add location_external_id column to disambiguate.")


class Command(BaseCommand):
    help = "Import Events from CSV (idempotent via event_external_id)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv_path"])
        if not csv_path.exists():
            raise SystemExit(f"File not found: {csv_path}")

        created = updated = skipped = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for line_no, row in enumerate(reader, start=2):
                try:
                    event_external_id = norm(row.get("event_external_id"))
                    if not event_external_id:
                        raise ValueError("Missing event_external_id")

                    title = norm(row.get("title"))
                    if not title:
                        raise ValueError("Missing title")

                    location = resolve_location(row)

                    start_date = parse_dt_flexible(row.get("start_date"))
                    if not start_date:
                        raise ValueError("Missing start_date")

                    # Your CSV uses 'end_data' (typo). Support both.
                    end_raw = norm(row.get("end_date")) or norm(row.get("end_data"))
                    end_date = parse_dt_flexible(end_raw) if end_raw else None

                    # Your CSV uses human labels. Map them.
                    raw_type = norm(row.get("event_type")).lower()
                    event_type = EVENT_TYPE_MAP.get(raw_type)
                    if not event_type:
                        raise ValueError(
                            f"Invalid event_type '{row.get('event_type')}'. "
                            f"Use one of: {list(EVENT_TYPE_MAP.keys())}"
                        )

                    description = norm(row.get("description"))
                    banner_image = normalize_url(row.get("banner_image"))
                    design_template_external_id = norm(row.get("design_template_external_id"))

                    obj, was_created = Event.objects.update_or_create(
                        event_external_id=event_external_id,
                        defaults={
                            
                            "event_external_id": event_external_id,
                            "title": title,
                            "location": location,
                            "start_date": start_date,
                            "end_date": end_date,
                            "event_type": event_type,
                            "description": description,
                            "banner_image": banner_image,
                            "design_template_external_id": design_template_external_id,
                        },
                    )

                    created += int(was_created)
                    updated += int(not was_created)

                except Exception as e:
                    skipped += 1
                    self.stdout.write(self.style.ERROR(f"Line {line_no}: {e} → skip"))

        self.stdout.write(self.style.SUCCESS(f"Done. created={created}, updated={updated}, skipped={skipped}"))
