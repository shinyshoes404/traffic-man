import requests, os, urllib.parse
from traffic_man.config import Config
from datetime import datetime

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
            resp_data = resp.json()
        except Exception as e:
            print(e)
            return None
        
        return resp_data
    
    @staticmethod
    def calc_traffic(google_maps_json: dict) -> dict:
        restructured_data = {}
        restructured_data["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        restructured_data["origin_addr"] = google_maps_json.get("origin_addresses")[0]
        restructured_data["destination_addr"] = google_maps_json.get("destination_addresses")[0]
        restructured_data["duration_sec"] = google_maps_json["rows"][0]["elements"][0]["duration"]["value"]
        restructured_data["duration_traffic_sec"] = google_maps_json["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
        restructured_data["traffic_ratio"] = round(restructured_data["duration_traffic_sec"]/restructured_data["duration_sec"] - 1, 3)

        return restructured_data

    