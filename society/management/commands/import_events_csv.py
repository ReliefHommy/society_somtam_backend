import csv
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from society.models import Event, Location


def norm(s: str) -> str:
    return (s or "").strip()


def normalize_url(url: str):
    url = norm(url)
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def parse_dt(value: str):
    """
    Accepts ISO like:
    - 2026-02-06T10:00:00Z
    - 2026-02-06T10:00:00+01:00
    - 2026-02-06 10:00:00
    """
    value = norm(value)
    if not value:
        return None

    dt = parse_datetime(value)
    if dt is None:
        # try plain date (YYYY-MM-DD)
        try:
            d = datetime.strptime(value, "%Y-%m-%d")
            dt = timezone.make_aware(d) if timezone.is_naive(d) else d
        except Exception:
            raise ValueError(f"Invalid datetime: {value}")

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


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

                    # CSV must provide a location reference:
                    # location_external_id == Location.related_store_external_id
                    location_external_id = norm(row.get("location_external_id"))
                    if not location_external_id:
                        raise ValueError("Missing location_external_id")

                    try:
                        location = Location.objects.get(related_store_external_id=location_external_id)
                    except Location.DoesNotExist:
                        raise ValueError(f"Location not found for related_store_external_id={location_external_id}")

                    start_date = parse_dt(row.get("start_date"))
                    if not start_date:
                        raise ValueError("Missing start_date")

                    end_date = parse_dt(row.get("end_date")) if norm(row.get("end_date")) else None

                    event_type = norm(row.get("event_type")).upper()
                    valid_types = {c[0] for c in Event.EventType.choices}
                    if event_type not in valid_types:
                        raise ValueError(f"Invalid event_type '{event_type}'. Must be one of: {sorted(valid_types)}")

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
