from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """command to wait for db to be available"""

    def handle(self, *args, **options):
        pass