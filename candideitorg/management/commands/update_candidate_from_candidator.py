# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from candideitorg.models import Candidate

class Command(BaseCommand):
    args = 'Candidate id'

    def handle(self, *args, **options):
        candidate_id = args[0]
        candidate = Candidate.objects.get(id=candidate_id)
        candidate.update()