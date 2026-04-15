from django.core.management.base import BaseCommand
from accounts.models import GoodreadsFeed
from accounts.views import fetch_rss_feed


class Command(BaseCommand):
    help = "Fetch all active Goodreads feeds"

    def handle(self, *args, **options):
        feeds = GoodreadsFeed.objects.filter(is_active=True)
        self.stdout.write(f"Fetching {feeds.count()} feeds...")

        for feed in feeds:
            self.stdout.write(f"  → {feed}")
            fetch_rss_feed(feed)

        self.stdout.write("Done.")
