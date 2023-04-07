import googlemaps, json

GOOGLE_API_KEY = "AIzaSyDRJupEkbEQLeofq7Njrv9al8SA-NrDdSA"
# I discovered that google maps allows airport codes,
# So using the google maps api for flight mapping.
# Unfortunately, google maps api does not allow flight routes (as far as I could tell).
# So using Geocoding api, and then plotting the points using pygmaps
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


def get_geocode(point):
    return gmaps.geocode()

