
from django.contrib.gis.db import models  # Essential for GeoDjango
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Location(models.Model):

    class Category(models.TextChoices):
        TEMPLE = 'TEMPLE', _('Temple')
        MARKET = 'MARKET', _('Thai Grocery/Market')
        RESTAURANT = 'RESTAURANT', _('Restaurant')
        PARTNER = 'PARTNER', _('Partner Venue')

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, 
        choices=Category.choices, 
        default=Category.TEMPLE
    )
    address = models.TextField(blank=True)
    # GeoDjango field for precise GPS mapping
    coordinates = models.PointField(srid=4326,geography=True) 
    website = models.URLField(blank=True, null=True)
    country_code = models.CharField(max_length=2, help_text="e.g. DE, FR, SE")

    related_store_external_id = models.CharField(max_length=100, blank=True)   #

    def __str__(self):
        return f"{self.name} ({self.country_code})"

class Event(models.Model):

    class EventType(models.TextChoices):
        RELIGIOUS = 'RELIGIOUS', _('Religious Ceremony')
        CONCERT = 'CONCERT', _('Concert/Entertainment')
        MARKET = 'MARKET', _('Market/Food Festival')
        COMMUNITY = 'COMMUNITY', _('Community Gathering')

    title = models.CharField(max_length=255)
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='events'
    )
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(null=True, blank=True)

    event_type = models.CharField(
        max_length=20, 
        choices=EventType.choices
    )
    description = models.TextField()
    banner_image = models.URLField(blank=True)

    design_template_external_id = models.CharField(max_length=100, blank=True)

 

    def __str__(self):
        return self.title

class MemberProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='somtam_profile'
    )
    home_city = models.CharField(max_length=100)
    interests = models.JSONField(default=list, blank=True)
    saved_events = models.ManyToManyField(
        Event, 
        blank=True, 
        related_name='interested_members'
    )

    def __str__(self):
        return f"Profile for {self.user.get_username()}"