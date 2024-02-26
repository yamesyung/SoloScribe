import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

data = pd.read_csv(r'/home/john/Desktop/worldcities.csv')

geolocator = Nominatim(user_agent="country_data")

countries_df = data[['country', 'iso2']]

countries_df = countries_df.drop_duplicates()
countries_df[['code_by_osm', 'address_type', 'latitude', 'longitude']] = ''

for index, row in countries_df.iterrows():
    country_name = row['country']
    search_query = f"{country_name}"

    try:
        location = geolocator.geocode(search_query, exactly_one=True, language="en", addressdetails=True)

        if location:
            countries_df.at[index, 'code_by_osm'] = location.raw['address'].get('country_code', None)
            countries_df.at[index, 'address_type'] = location.raw.get('addresstype', None)
            countries_df.at[index, 'latitude'] = location.latitude
            countries_df.at[index, 'longitude'] = location.longitude
            sleep(1)

    except Exception as e:

        print(f"Error geocoding {country_name}: {str(e)}")


countries_df.to_csv('worldcountries.csv')