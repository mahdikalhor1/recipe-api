from django.core.management.base import BaseCommand
import time
from django.db.utils import OperationalError
from psycopg2 import OperationalError as psycopg2Err
class Command(BaseCommand):
    """command to wait for db to be available"""

    def handle(self, *args, **options):
        self.stdout.write('Wainting for db to be available...')

        is_not_ready=True

        while is_not_ready:

            try:
                self.check(databases=['default'])
                is_not_ready = False
            except (OperationalError, psycopg2Err):
                self.stdout.write('Unavailable, waiting 1 second...')
                time.sleep(0.025)

        self.stdout.write('database is available now.')