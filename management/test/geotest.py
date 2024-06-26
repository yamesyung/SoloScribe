from geopy.geocoders import Nominatim
from pprint import pprint

# Instantiate a new Nominatim client
geolocator = Nominatim(user_agent="bookstats")

# Get location raw data from the user
your_loc = input("Enter your location: ")
location = geolocator.geocode(your_loc, exactly_one=True, language="en", addressdetails=True)

# Print raw data
pprint(location.raw)
pprint(location.raw['address']['country_code'])

pprint(location.raw.get('addresstype'))
pprint(location.raw['addresstype'])
pprint(location.raw['lat'])
pprint(location.raw['lon'])

