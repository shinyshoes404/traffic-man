import pandas as pd
from traffic_man.config import Config

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class TrafficDataProc:
    def __init__(self, traffic_data: list):
        self.traffic_data = traffic_data    

    def _build_df(self) -> bool:
        try:
            self.df = pd.DataFrame(self.traffic_data)
        except Exception as e:
            logger.error("problem creating data frame")
            logger.error(e)
            return None        
        return True
    
    def _create_orig_dest_col(self):
        try:
            self.df["orig_dest_combined"] = self.df["orig_place_id"] + "|" + self.df["dest_place_id"]
        except Exception as e:
            logger.error("problem combining origin and dest place id columns in dataframe")
            logger.error(e)
            return None        
        return True
    
    def _get_bad_traffic(self) -> list:
        try:
            bad_traffic_list = self.df.query("traffic_ratio >= " + str(Config.overage_parameter)).to_dict('records')
        except Exception as e:
            logger.error("problem getting bad traffic records")
            logger.error(e)
            return None
        return bad_traffic_list
    
