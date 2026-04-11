import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


WEEK_START_CHOICES = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

QUOTES_LAYOUT_CHOICES = [
    ('grid', 'Grid'),
    ('list', 'List'),
]


def get_default_theme():
    """
    used to set the default theme when a new profile is created
    """
    theme, _ = Theme.objects.get_or_create(name="default")
    return theme


class CustomUser(AbstractUser):

    def get_theme_name(self):
        """
        used to have access to profile's selected theme in templates
        """
        if hasattr(self, "preferences") and self.preferences and self.preferences.preferred_theme:
            return self.preferences.preferred_theme.name
        return "default"

    pass


class Theme(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class UserPreferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    preferred_theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True,
                                        default=get_default_theme)
    gallery_cover_size = models.IntegerField(default=150)
    week_start = models.IntegerField(choices=WEEK_START_CHOICES, default=0)  # monday
    quotes_layout = models.CharField(max_length=10, choices=QUOTES_LAYOUT_CHOICES, default='grid')

    def __str__(self):
        return f"Preferences for {self.user.username}"


class GoodreadsFeed(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="feeds")
    feed_url = models.URLField(max_length=500)
    display_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    cache_file = models.CharField(max_length=512, blank=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    last_fetch_error = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "feed_url")  # prevent duplicate subscriptions per user
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name or self.feed_url


class BookUpdate(models.Model):
    feed = models.ForeignKey(GoodreadsFeed, on_delete=models.CASCADE, related_name="updates")

    # identifiers
    guid = models.CharField(max_length=500)
    book_id = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=20, null=True, blank=True)

    # book info
    book_title = models.CharField(max_length=500, blank=True)
    book_author = models.CharField(max_length=255, blank=True)
    book_description = models.TextField(blank=True)
    book_published = models.CharField(max_length=20, blank=True)
    num_pages = models.PositiveIntegerField(null=True, blank=True)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # cover images
    book_image_url = models.URLField(max_length=500, blank=True)
    book_medium_image_url = models.URLField(max_length=500, blank=True)
    book_large_image_url = models.URLField(max_length=500, blank=True)
    book_image_local = models.CharField(max_length=512, blank=True)

    # user activity
    user_name = models.CharField(max_length=255, blank=True)
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    user_review = models.TextField(blank=True)
    user_shelves = models.CharField(max_length=500, blank=True)
    user_read_at = models.DateTimeField(null=True, blank=True)
    user_date_added = models.DateTimeField(null=True, blank=True)

    # feed metadata
    book_url = models.URLField(max_length=500, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("feed", "guid")
        ordering = ["-published_at"]

    def __str__(self):
        return f"{self.book_title} by {self.book_author}"
