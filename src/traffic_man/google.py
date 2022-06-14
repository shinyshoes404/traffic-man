import requests, os, urllib.parse, logging
from traffic_man.config import Config
from datetime import datetime
from time import sleep


# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

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
    model = Config.traffic_model
    params_urlencode = urllib.parse.urlencode(params, safe=":/")
    
    @staticmethod
    def call_google_maps():
        logger.info("attempting to call google maps api")

        try:
            resp = requests.get(url=MapGoogler.base_url + MapGoogler.params_urlencode)
            resp_data = resp.json()
        except requests.exceptions.Timeout:
            logger.warning("google maps api request timed out")
            return None
        except requests.exceptions.SSLError:
            logger.warning("google maps api request experienced SSL error")
            return None
        except Exception as e:
            logger.error("google maps api request experienced an unexpected exception")
            logger.error(e)
            return None
        
        if resp.status_code != 200:
            logger.error("problem with google maps request status code: {0} content: {1}".format(resp.status_code, resp.content))
            return None
        
        logger.info("google maps data retreived")
        return resp_data
    
    @staticmethod
    def google_call_with_retry(attempts: int) -> dict:
        # attempts = total attempts, not just retries
        for i in range(0,attempts):
            raw_maps_data = MapGoogler.call_google_maps()
            if raw_maps_data:
                return raw_maps_data
            if i < max(range(0, attempts)):
                logger.warning("wait before we retry retry")
                sleep(10 * (i + 1))
                logger.warning("retrying google maps api call")

        return None
    
    @staticmethod
    def calc_traffic(google_maps_json: dict) -> dict:
        restructured_data = {}

        try:
            restructured_data["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            restructured_data["origin_addr"] = google_maps_json.get("origin_addresses")[0]
            restructured_data["destination_addr"] = google_maps_json.get("destination_addresses")[0]
            restructured_data["duration_sec"] = google_maps_json["rows"][0]["elements"][0]["duration"]["value"]
            restructured_data["duration_traffic_sec"] = google_maps_json["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
            restructured_data["traffic_ratio"] = round(restructured_data["duration_traffic_sec"]/restructured_data["duration_sec"] - 1, 3)
        except Exception as e:
            logger.error("problem calculating traffic")
            logger.error(e)
            return None
        
        return restructured_data

    