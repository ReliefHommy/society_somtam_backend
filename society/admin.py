from django.contrib import admin
from django.contrib.gis import admin as gis_admin  # <-- add this
from .models import Location, Event, MemberProfile


@admin.register(Location)
class LocationAdmin(gis_admin.GISModelAdmin):  # <-- change ModelAdmin -> GISModelAdmin
    list_display = ("name", "category", "country_code","coordinates","related_store_external_id")
    list_filter = ("category", "country_code")
    search_fields = ("name", "address")

    # Optional (nice defaults for Europe view)
    default_zoom = 5
    default_lon = 10
    default_lat = 50


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "start_date", "location","design_template_external_id","event_external_id")
    list_filter = ("event_type", "start_date")
    search_fields = ("title", "description", "location__name")


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "home_city")

