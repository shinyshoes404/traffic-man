import sqlalchemy as db

from traffic_man.db.models import check_times, holidays, check_days
from traffic_man.config import Config
import logging

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class DataSetup:
    def __init__(self, engine):
        self.engine = engine

    def update_check_times(self):
        logger.info("deleting all data from the check_time table")
        
        try:
            # clear data from the check_times table
            qry = db.delete(check_times)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from check_times")
            logger.error(e)
            return None

        logger.info("adding this data to the check_times table {0}".format(Config.traffic_check_times))
        try:
            # populate times from Config
            for time in Config.traffic_check_times:            
                qry = check_times.insert().values(time=time)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting times into check_times table")
            logger.error(e)
            return None
        
        return True

    def update_holidays(self):
        logger.info("deleting all data from the holidays table")

        try:
            # clear data from the holidays table
            qry = db.delete(holidays)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from holidays")
            logger.error(e)
            return None
        
        logger.info("adding these dates to the holiday table {0}".format(Config.holidays))

        try:
            # populate holidays from Config
            for date in Config.holidays:
                qry = holidays.insert().values(date=date)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem writing dates to holidays table")
            logger.error(e)
            return None

        return True
    
    def update_check_days(self):
        logger.info("deleting data from check_days table")

        try:
            # clear data from the check_days table
            qry = db.delete(check_days)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from check_days table")
            logger.error(e)
            return None
        
        logger.info("adding these days to the check_days table {0}".format(Config.traffic_check_days))
        try:
            # populate days to check
            for day_of_week in Config.traffic_check_days:
                qry = check_days.insert().values(check_days=day_of_week)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting data to check_days table")
            logger.error(e)
            return None
        
        return True