from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import GoodreadsFeed
from accounts.views import fetch_rss_feed


class Command(BaseCommand):
    help = "Fetch all active Goodreads feeds"

    def handle(self, *args, **options):

        threshold = timezone.now() - timedelta(hours=7)

        feeds = GoodreadsFeed.objects.filter(
            is_active=True,
            last_fetched_at__lt=threshold,
            user__last_login__gte=timezone.now() - timedelta(days=7)
        )
        self.stdout.write(f"Fetching {feeds.count()} feeds...")

        for feed in feeds:
            self.stdout.write(f"  → {feed}")
            fetch_rss_feed(feed)

        self.stdout.write("Done.")
