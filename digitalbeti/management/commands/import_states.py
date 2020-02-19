from django.core.management.base import BaseCommand
from django.utils import timezone

from digibeti import settings
from digitalbeti.models import VillageDetails


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        state_files = open(settings.BASE_DIR + '/bin/states.csv')
        for record in state_files:
            try:
                data = record.split(',')
                v = VillageDetails()
                v.state = data[0].upper().strip()
                v.district = data[1].upper().strip()
                v.subdistrict = data[2].upper().strip()
                v.village = data[3].upper().strip()
                v.save()
            except:
                print('Duplicate', record)
