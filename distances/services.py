import requests

from django.conf import settings
from distances.models import Place


def _fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_address_coordinates(address):
    place, created = Place.objects.get_or_create(address=address)

    if not created:
        return place.latitude, place.longitude

    place_coordinates = _fetch_coordinates(settings.YANDEX_API_KEY, address)
    if not place_coordinates:
        return None

    place.address = address
    place.latitude, place.longitude = place_coordinates
    place.save()
    return place.latitude, place.longitude
