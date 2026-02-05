import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from society.models import Location


CATEGORY_MAP = {
    "temple": Location.Category.TEMPLE,
    "market": Location.Category.MARKET,
    "restaurant": Location.Category.RESTAURANT,
    "partner": Location.Category.PARTNER,
}


def normalize_website(url: str):
    url = (url or "").strip()
    if not url:
        return None
    # CSV may have "www.stm-society.com" (no scheme)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def parse_point_lat_lng(s: str) -> Point:
    """
    CSV stores: 'lat, lng'
    GeoDjango Point expects: (lon, lat)
    """
    raw = (s or "").strip()
    if not raw:
        raise ValueError("Missing coordinates")
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinates format: {raw}")
    lat = float(parts[0])
    lng = float(parts[1])
    return Point(lng, lat, srid=4326)


class Command(BaseCommand):
    help = "Import Locations from a CSV file (idempotent via related_store_external_id)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv_path"])
        if not csv_path.exists():
            raise SystemExit(f"File not found: {csv_path}")

        created = 0
        updated = 0
        skipped = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=2):  # header is line 1
                try:
                    name = (row.get("name") or "").strip()
                    if not name:
                        self.stdout.write(self.style.WARNING(f"Line {i}: missing name → skip"))
                        skipped += 1
                        continue

                    category_raw = (row.get("category") or "").strip().lower()
                    category = CATEGORY_MAP.get(category_raw, Location.Category.TEMPLE)

                    address = (row.get("address") or "").strip()
                    country_code = (row.get("country_code") or "").strip().upper()
                    website = normalize_website(row.get("website") or "")

                    coords = parse_point_lat_lng(row.get("coordinates") or "")

                    # Unique key (preferred)
                    ext_id = (row.get("related_store_external_id") or "").strip()

                    if ext_id:
                        lookup = {"related_store_external_id": ext_id}
                    else:
                        # Fallback: avoid duplicates if ext_id missing
                        lookup = {"name": name, "country_code": country_code}

                    obj, was_created = Location.objects.update_or_create(
                        **lookup,
                        defaults={
                            "name": name,
                            "category": category,
                            "address": address,
                            "coordinates": coords,
                            "website": website,
                            "country_code": country_code,
                            "related_store_external_id": ext_id,  # <-- IMPORTANT: save it too
                        },
                    )

                    created += int(was_created)
                    updated += int(not was_created)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Line {i}: {e} → skip"))
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Done. created={created}, updated={updated}, skipped={skipped}"))

