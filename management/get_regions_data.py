import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

regions_df = pd.read_csv(r'/home/john/Desktop/worldregions.csv')

geolocator = Nominatim(user_agent="region_data")

regions_df[['latitude', 'longitude']] = ''

for index, row in regions_df.iterrows():
    region_name = row['query']
    search_query = f"{region_name}"

    try:
        location = geolocator.geocode(search_query, exactly_one=True, language="en", addressdetails=True)

        if location:
            regions_df.at[index, 'latitude'] = location.latitude
            regions_df.at[index, 'longitude'] = location.longitude
            sleep(1)

    except Exception as e:

        print(f"Error geocoding {region_name}: {str(e)}")


regions_df.to_csv('worldregions.csv')