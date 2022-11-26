import sqlalchemy as db

from traffic_man.db.models import phone_numbers, traffic_data, traffic_conditions
from traffic_man.config import Config
from datetime import datetime
import logging

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class UserData:
    def __init__(self, engine):
        self.engine = engine

    def get_orig_dest_pairs(self) -> list:
        try:
            qry = db.select([phone_numbers.c.origin_place_id,
                            phone_numbers.c.dest_place_id]
                            ).where(phone_numbers.c.status == "sub", phone_numbers.c.auth_status == "auth"
                            ).distinct()

            with self.engine.connect() as connection:
                results_obj = connection.execute(qry)
                results_data = results_obj.fetchall()
        except Exception as e:
            logger.error("problem getting place ids")
            logger.error(e)
            return False
        
        if len(results_data) == 0:
            logger.info("no active place id pairs are present in the table")
            return None
        
        place_id_pairs = []
        for row in results_data:
            place_id_pairs.append([row[0], row[1]])
        
        logger.info("retrieved these place id pairs \n {0}".format(place_id_pairs))
        return place_id_pairs
    
    def get_sub_phone_numbers_by_orig_dest_pair(self, orig_dest_pair: list):
        try:
            qry = phone_numbers.select([phone_numbers.c.phone_num]
            ).where(phone_numbers.c.status == "sub",
                    phone_numbers.c.auth_status == "auth",
                    phone_numbers.c.origin_place_id == orig_dest_pair[0],
                    phone_numbers.c.dest_place_id == orig_dest_pair[1]
            )
        
            with self.engine.conect() as connection:
                results_obj = connection.execute(qry)
                results_data = results_obj.fetchall()
        except Exception as e:
            logger.error("problem getting phone numbers")
            logger.error(e)
            return False
        
        if len(results_data) == 0:
            logger.info("no phone numbers found")
            return None
        
        logger.info("found {0} subcribed and authorized phone numbers for origin id {1} and dest id {2}".format(len(results_data), orig_dest_pair[0], orig_dest_pair[1]))
        return results_data
