from traffic_man.db.models import sms_data 
from traffic_man.config import Config
from datetime import datetime
import logging

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSData:
    def __init__(self, engine):
        self.engine = engine
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
    
    def check_sms_today(self, type: str) -> bool:
        try:
            qry = sms_data.select().where(sms_data.c.date == self.curr_date, sms_data.c.sms_type == type)
            with self.engine.connect() as connection:
                result_obj = connection.execute(qry)
                results_data = result_obj.fetchall()
        except Exception as e:
            logger.error("problem getting sms records")
            logger.error(e)
            return None
        
        if len(results_data) == 0:
            logger.info("no {0} sms messages yet today".format(type))
            return False
        
        logger.info("{0} {1} sms already today".format(len(results_data), type))
        return results_data
        

    def write_sms_records(self, sms_data: list) -> bool:
        logger.info("attempting to add {0} sms records for {1}".format(len(sms_data), self.curr_date))
        try:
            qry = sms_data.insert().values(sms_data)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting sms records")
            logger.error(e)
            return None
        
        return True