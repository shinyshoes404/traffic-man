import requests, os, urllib.parse, logging, copy
from traffic_man.config import Config
from datetime import datetime
from time import sleep


# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class MapGoogler:

    def __init__(self, origin_list:str, dest_list:str):
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        # expecting origin_list and dest_list to be strings of the format "place_id:abc1234|place_id:def5678"
        self.params = {            
            "origins": origin_list,
            "destinations": dest_list,
            "traffic_model": Config.traffic_model,
            "mode": Config.mode,
            "language": Config.language,
            "departure_time": "now",
            "key": os.environ.get("GOOGLE_API_KEY")
        }

        self.params_urlencode = urllib.parse.urlencode(self.params, safe=":/")
    
    def _call_google_maps(self):
        logger.info("attempting to call google maps api")

        try:
            resp = requests.get(url=self.base_url + self.params_urlencode)
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
    
    def google_call_with_retry(self, attempts: int) -> dict:
        # attempts = total attempts, not just retries
        for i in range(0,attempts):
            raw_maps_data = self._call_google_maps()
            if raw_maps_data:
                return raw_maps_data
            if i < max(range(0, attempts)):
                logger.warning("wait before we retry retry")
                sleep(10 * (i + 1))
                logger.warning("retrying google maps api call")

        return None
    
    @staticmethod
    def build_orig_dest_lists(orig_dest_set):
        # assumes orig_dest_set follows the structure [[orig1, orig2], 3, [[dest1], [dest2, dest3]]]
   
        orig_list = ""
        for orig in orig_dest_set[0]:
            if len(orig_list) > 0:
                orig_list = orig_list + "|" + "place_id:" + orig
            else:
                orig_list = "place_id:" + orig 
        
        dest_list = ""
        for dest_set in orig_dest_set[2]:
            for dest in dest_set:
                if len(dest_list) > 0:
                    dest_list = dest_list + "|" + "place_id:" + dest
                else:
                    dest_list = "place_id:" + dest
        
        return orig_list, dest_list


    @staticmethod
    def calc_traffic(google_maps_json: dict, orig_dest_set: list) -> list:
        # expecting raw google maps repsonse as json and the origin destination set used for the request
        dest_counts = MapGoogler._get_dest_counts(orig_dest_set)
        structured_data = MapGoogler._extract_data(dest_counts, google_maps_json, orig_dest_set)
        if structured_data == None:
            return None
        return structured_data

    @staticmethod
    def _get_dest_counts(orig_dest_set) -> list:
        # assumes orig_dest_set follows the structure [[orig1, orig2], 3, [[dest1], [dest2, dest3]]]
        dest_counts = []
        for dest_list in orig_dest_set[2]:
            dest_counts.append(len(dest_list))
        
        return dest_counts
    
    @staticmethod
    def _extract_data(dest_counts: list, google_maps_json: dict, origin_dest_set: list) -> list:
        
        rows = google_maps_json.get("rows")
        if rows == None:
            logger.error("failed to extract rows from google maps json")
            return None
        
        if len(rows) < 1:
            logger.error("zero rows in google maps json")
            return None

        i = 0
        dest_counter = 0
        curr_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        traffic_data = []
        for dest_count in dest_counts:
            elements = google_maps_json["rows"][i]["elements"][dest_counter:dest_counter + dest_count]
            dest_addresses = google_maps_json["destination_addresses"][dest_counter:dest_counter + dest_count]
            dest_counter = dest_counter + dest_count
            # counter for the sliced element data
            j = dest_counter
            # counter for the origin_dest_set destinations list
            k = 0
            for element in elements:
                try:
                    temp_data = {}
                    temp_data["datetime"] = curr_date_time
                    temp_data["origin_addr"] = google_maps_json["origin_addresses"][i]
                    temp_data["destination_addr"] = dest_addresses[k]
                    temp_data["duration_sec"] = element["duration"]["value"]
                    temp_data["duration_traffic_sec"] = element["duration_in_traffic"]["value"]
                    temp_data["traffic_ratio"] = round(temp_data["duration_traffic_sec"]/temp_data["duration_sec"] -1, 3)
                    temp_data["orig_place_id"] = origin_dest_set[0][i]
                    temp_data["dest_place_id"] = origin_dest_set[2][i][k]

                    j += 1
                    k += 1

                    traffic_data.append(copy.deepcopy(temp_data))
                except Exception as e:
                    logger.error("problem extracting data from google json")
                    logger.error(e)
                    logger.error("\t\t\t google json: {0}".format(google_maps_json))
                    logger.error("\t\t\t traffic_data: {0}".format(traffic_data))
                    return None

            i += 1
        
        return traffic_data        