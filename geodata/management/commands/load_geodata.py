import os
import pandas as pd
from geodata.models import Country, City
from django.core.management.base import BaseCommand

"""
    function that loads the csv data into db
    used when container is starting
"""


class Command(BaseCommand):
    help = 'Import data from CSV files using pandas'

    def handle(self, *args, **options):

        directory = os.path.dirname(os.path.realpath(__file__))

        if Country.objects.exists():
            self.stdout.write(self.style.SUCCESS('Table is not empty. Skipping countries import.'))
        else:
            df_countries = pd.read_csv(directory + '/worldcountries.csv')
            Country.objects.bulk_create(
                Country(
                    name=row['country'],
                    code=row['iso2'],
                    latitude=row['latitude'],
                    longitude=row['longitude']
                )
                for index, row in df_countries.iterrows()
            )
            self.stdout.write(self.style.SUCCESS('Countries data imported successfully'))

        if City.objects.exists():
            self.stdout.write(self.style.SUCCESS('Table is not empty. Skipping cities import.'))
        else:
            df_cities = pd.read_csv(directory + '/worldcities.csv')
            df_cities.fillna(0, inplace=True)
            City.objects.bulk_create(
                City(
                    city_name=row['city'],
                    admin_name=row['admin_name'],
                    country=row['country'],
                    code=row['iso2'],
                    latitude=row['lat'],
                    longitude=row['lng'],
                    population=row['population']
                )
                for index, row in df_cities.iterrows()
            )
            self.stdout.write(self.style.SUCCESS('Cities data imported successfully'))
