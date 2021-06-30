import os
import json
import requests
from shapely.geometry import shape
import pygeos as pg

class ValhallaException(Exception):
    """Raised when Valhalla service returns error."""

class Valhalla:

    def __init__(self, url=None):
        self.url = url if url is not None else os.environ['VALHALLA_URL']

    def isochrone(self, lat, lon, distance=None, time=None, costing="auto"):
        contours = [{"distance": distance}] if distance is not None else [{"time": time}]
        locations = [{"lat": lat, "lon": lon}]
        request_json = {"locations": locations, "polygons": True, "costing": costing, "contours": contours}
        request_json = json.dumps(request_json)
        r = requests.get(self.url + '/isochrone?json=' + request_json)
        geom = r.json()
        try:
            wkt = shape(geom['features'][0]['geometry']).to_wkt()
        except KeyError:
            raise ValhallaException(geom['error'])
        return pg.from_wkt(wkt)
