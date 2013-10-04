# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from candideitorg.models import Election

class Command(BaseCommand):
    args = ''

    def handle(self, *args, **options):
        Election.fetch_all_from_api()