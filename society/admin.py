from django.contrib import admin
from .models import Location, Event, MemberProfile

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "country_code")
    list_filter = ("category", "country_code")
    search_fields = ("name", "address")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "start_date", "location")
    list_filter = ("event_type", "start_date")
    search_fields = ("title", "description", "location__name")

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "home_city")

