import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

places_df = pd.read_csv(r'/home/john/Desktop/otherplaces.csv')

geolocator = Nominatim(user_agent="other_data")

for index, row in places_df.iterrows():
    place_name = row['name']
    search_query = f"{place_name}"

    try:
        location = geolocator.geocode(search_query, exactly_one=True, language="en", addressdetails=True)

        if location:
            places_df.at[index, 'latitude'] = location.latitude
            places_df.at[index, 'longitude'] = location.longitude
            sleep(1)

    except Exception as e:

        print(f"Error geocoding {place_name}: {str(e)}")

places_df.to_csv('places.csv')
