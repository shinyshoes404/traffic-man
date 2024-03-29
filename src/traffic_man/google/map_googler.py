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


class Googler:
    def __init__(self):
        self.googler_type = None
        self.params = None
        self.base_url = None
        self.params_urlencode = None
        
        
    def _encode_params(self) -> None:
        self.params_urlencode = urllib.parse.urlencode(self.params, safe=":/")

    def _call_google_api(self) -> dict:
        logger.info("attempting to call google {0} api".format(self.googler_type))

        try:
            resp = requests.get(url=self.base_url + self.params_urlencode)
            resp_data = resp.json()
        except requests.exceptions.Timeout:
            logger.warning("google {0} api request timed out".format(self.googler_type))
            return None
        except requests.exceptions.SSLError:
            logger.warning("google {0} api request experienced SSL error".format(self.googler_type))
            return None
        except Exception as e:
            logger.error("google {0} api request experienced an unexpected exception".format(self.googler_type))
            logger.error(e)
            return None
        
        if resp.status_code != 200:
            logger.error("problem with google {0} request status code: {1} content: {2}".format(self.googler_type, resp.status_code, resp.content))
            return None
        
        logger.info("google {0} api data retreived".format(self.googler_type))
        return resp_data
    
    def google_call_with_retry(self, attempts: int) -> dict:
        # attempts = total attempts, not just retries
        for i in range(0,attempts):
            raw_data = self._call_google_api()
            if raw_data:
                return raw_data
            if i < max(range(0, attempts)):
                logger.warning("wait before we retry")
                sleep(10 * (i + 1))
                logger.warning("retrying google {0} api call".format(self.googler_type))

        return None


class PlaceFinder(Googler):
    def __init__(self, search_text: str):        
        super().__init__()
        self.googler_type = "place-finder"
        self.params = {
            "input": search_text,
            "fields": "formatted_address,type,place_id",
            "inputtype": "textquery",
            "key": os.environ.get("GOOGLE_PLACES_API_KEY"),
            "locationbias": "".join(filter(None, ["circle:", os.environ.get("GOOGLE_PLACES_RADIUS_METERS"), "@", os.environ.get("GOOGLE_PLACES_LATITUDE"), ",", os.environ.get("GOOGLE_PLACES_LONGITUDE")]))
        }     

        self.base_url = Config.place_finder_base_url   
        self._encode_params()
    
    def search_for_place_id(self):
        search_data = self.google_call_with_retry(2)
        if not search_data:
            return { "search_status": "api error", "msg": "encountered an error with the api", "addr": None, "place_id": None, "results_count": 0 }
        if search_data.get("status") == "ZERO_RESULTS":
            return { "search_status": "no results", "msg": "no reults returned for search", "addr": None, "place_id": None, "results_count": 0}
        if search_data.get("status") == "OK":
            return {
                "search_status" : "ok", 
                "msg" : "found results",
                "addr": search_data.get("candidates")[0].get("formatted_address"),
                "place_id": search_data.get("candidates")[0].get("place_id"),
                "results_count": len(search_data.get("candidates"))
            }
        
        return { "search_status": "unknown error", "msg": "encountered and unknown error", "addr": None,  "place_id": None, "results_count": 0}
    
        

class MapGoogler(Googler):

    def __init__(self, origin_list:str, dest_list:str):
        super().__init__()
        self.googler_type = "maps"
        self.base_url = Config.distance_matrix_base_url
        # expecting origin_list and dest_list to be strings of the format "place_id:abc1234|place_id:def5678"
        self.params = {            
            "origins": origin_list,
            "destinations": dest_list,
            "traffic_model": Config.traffic_model,
            "mode": Config.mode,
            "language": Config.language,
            "departure_time": "now",
            "key": os.environ.get("GOOGLE_DISTANCE_MATRIX_API_KEY")
        }
        
        self._encode_params()
    
    
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