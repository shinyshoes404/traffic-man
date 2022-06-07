import requests, os, urllib.parse
from traffic_man.config import Config

class MapGoogler:
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    params = {
        "origins": "place_id:" + os.environ.get("ORIGIN_PLACE_ID"),
        "destinations": "place_id:" + os.environ.get("DEST_PLACE_ID"),
        "traffic_model": Config.traffic_model,
        "mode": Config.mode,
        "language": Config.language,
        "departure_time": "now",
        "key": os.environ.get("GOOGLE_API_KEY")
    }

    params_urlencode = urllib.parse.urlencode(params, safe=":/")
    
    @staticmethod
    def call_google_maps():
        try:
            resp = requests.get(url=MapGoogler.base_url + MapGoogler.params_urlencode)
        except Exception as e:
            print(e)
        
        print(resp.json())

    