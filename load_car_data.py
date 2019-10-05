from csv import DictReader
from datetime import datetime

from django.core.management import BaseCommand

from servicing.models import Car, Service
from pytz import UTC


DATETIME_FORMAT = '%m/%d/%Y %H:%M'

SERVICE_NAMES = [
    'WASH',
    'CLEAN',
    'ENGINE OIL',
    'ESSENTIAL SERVICE',
    'INTERIM SERVICE',
    'BRAKE SHOE',
    'DEEP CLEAN'
]




ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the pet data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""




class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from car_data.csv into our Car model"

    def handle(self, *args, **options):
        if Service.objects.exists() or Car.objects.exists():
            print('Car data already loaded...exiting.')
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return
        print("Creating services data")
        for service_name in SERVICE_NAMES:
            vac = Service(name=service_name)
            vac.save()
        print("Loading car data for cars available for service")
        for row in DictReader(open('./car_data.csv')):
            car = Car()
            car.car_model = row['CAR_MODEL']
            car.car_owner = row['CAR_OWNER']
            car.car_notes = row['NOTES']
            car.car_number = row['CAR_NUMBER']
            car.description = row['Car Description']
            car.service_type = row['TYPE']
            car.year_old = row['OLD']
            raw_submission_date = row['submission date']
            submission_date = UTC.localize(
                datetime.strptime(raw_submission_date, DATETIME_FORMAT))
            car.submission_date = submission_date
            car.save()
            raw_service_names = row['services']
            service_names = [name for name in raw_service_names.split('| ') if name]
            for ser_name in service_names:
                ser = Service.objects.get(name=ser_name)
                car.servicing.add(ser)
            car.save()