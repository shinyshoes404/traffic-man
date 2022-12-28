import pandas as pd
import numpy as np
from traffic_man.config import Config

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class TrafficDataProc:
    def __init__(self, struct_google_traffic_data: list, traffic_conditions_data: dict):
        self.traffic_data = struct_google_traffic_data
        if traffic_conditions_data == {}:
            # dummy data to avoid errors
            self.traffic_conditions_data = {"NoPlaceID": "NoData"}
        else:
            self.traffic_conditions_data = traffic_conditions_data

    def _build_google_traffic_data_df(self) -> bool:
        try:
            self.google_data_df = pd.DataFrame(self.traffic_data)
        except Exception as e:
            logger.error("problem creating data frame")
            logger.error(e)
            return None        
        return True
    
    def _create_orig_dest_col(self):
        try:
            self.google_data_df["orig_dest_combined"] = self.google_data_df["orig_place_id"] + "|" + self.google_data_df["dest_place_id"]
        except Exception as e:
            logger.error("problem combining origin and dest place id columns in dataframe")
            logger.error(e)
            return None        
        return True
    
    def _build_traffic_condition_df(self):
        # expecting a dictionary of the format {"origplaceid1|destplaceid1": "traffic", "originplaceid2|destplaceid2": "traffic_resolved"}
        try:
            self.traffic_conditions_df = pd.DataFrame(self.traffic_conditions_data.items(), columns = ["orig_dest_placeids", "traffic_condition"])
        except Exception as e:
            logger.error("problem creating taffic condition data frame")
            logger.error(e)
            return None        
        return True
    
    def build_dfs(self) -> bool:
        build_google = self._build_google_traffic_data_df()
        create_orig_dest = self._create_orig_dest_col()
        build_traff_cond = self._build_traffic_condition_df()

        if build_google and create_orig_dest and build_traff_cond:
            return True
        
        return None
    
    def get_new_bad_traffic(self) -> list:
        # returns a list of objects
        new_bad_traff_res_list = []
        try:
            # get all bad traffic orig dest pairs that don't have a bad traffic entry yet today
            bad_traff_res = self.google_data_df.query("traffic_ratio >= " + str(Config.overage_parameter))
            if not bad_traff_res.empty:
                merged_df = pd.merge(bad_traff_res,
                                                self.traffic_conditions_df,
                                                left_on = ["orig_dest_combined"],
                                                right_on = ["orig_dest_placeids"],
                                                how = "left"
                                                )
                if not merged_df.empty:
                    new_bad_traff_res = merged_df.query("traffic_condition.isnull()")

                    if not new_bad_traff_res.empty:

                        # replace nan with None
                        new_bad_traff_res.replace({np.nan:None}, inplace=True)

                        # convert the result data frame into a list of objects that is easy to insert into the db
                        new_bad_traff_res_list = new_bad_traff_res.to_dict("records")

                       
        except Exception as e:
            logger.error("problem getting new bad traffic records")
            logger.error(e)
            return None

        return new_bad_traff_res_list
    
    def get_resolved_traffic(self) -> list:

        new_resolved_traff_res_list = []
        # returns a list of objects
        try:
            # get all bad traffic orig dest pairs that don't have a bad traffic entry yet today
            below_threshold = self.google_data_df.query("traffic_ratio <= " + str(.5 * Config.overage_parameter))
            if not below_threshold.empty:
                join_df = pd.merge(below_threshold,
                                                self.traffic_conditions_df,
                                                left_on = ["orig_dest_combined"],
                                                right_on = ["orig_dest_placeids"],
                                                how = "inner"
                                                )
                if not join_df.empty:                                            
                    new_resolved_traff_res = join_df.query("traffic_condition == 'traffic'")
 

                    if not new_resolved_traff_res.empty:
                
                        # convert the result data frame into a list of objects that is easy to insert into the db
                        new_resolved_traff_res_list = new_resolved_traff_res.to_dict("records")

                       
        except Exception as e:
            logger.error("problem getting new resolve traffic records")
            logger.error(e)
            return None

        return new_resolved_traff_res_list
    


    

    


    
