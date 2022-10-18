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

class TrafficData:
    def __init__(self, engine):
        self.engine = engine
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
    
    def store_traffic_data(self, traffic_json: dict) -> bool:

        qry = traffic_data.insert().values(
            datetime=traffic_json["datetime"],
            origin_place_id=traffic_json["origin_place_id"],
            origin_addr=traffic_json["origin_addr"],
            dest_place_id=traffic_json["dest_place_id"],
            destination_addr=traffic_json["destination_addr"],
            duration_sec=traffic_json["duration_sec"],
            duration_traffic_sec=traffic_json["duration_traffic_sec"],
            traffic_ratio=traffic_json["traffic_ratio"]
            )

        try:
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem storing traffic data")
            logger.error(e)
            return None

        logger.info("stored this traffic data in the traffic_data table {0}".format(traffic_json))
        return True

    def check_traffic_conditions(self) -> dict:

        try:
            qry = traffic_conditions.select().where(traffic_conditions.c.date == self.curr_date)
            with self.engine.connect() as connection:
                results = connection.execute(qry)
                rows = results.fetchall()
        except Exception as e:
            logger.error("problem checking traffic conditions in the db")
            logger.error(e)
            return False

        if len(rows) == 0:
            logger.info("no traffic conditions listed for today")
            return None
        
        traffic_results = {}
        for row in rows:
            if row[5]:
                traffic_cond = "traffic_resolved"
            else:
                traffic_cond = "traffic"

            # create at an object to the traffic results dict with the format {"orig_place_id|dest_place_id" : "traffic_cond"}
            traffic_results[row[2] + "|" + row[3]] = traffic_cond

        return traffic_results
 
    
    def write_bad_traffic(self, orig_place_id: str, dest_place_id: str) -> bool:
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            qry = traffic_conditions.insert().values(
                date=self.curr_date, 
                bad_traffic_datetime=curr_datetime,
                orig_place_id=orig_place_id,
                dest_place_id=dest_place_id
                )

            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem writing back trafic record for orig id: {1}, dest_id: {2}".format(orig_place_id, dest_place_id))
            logger.error(e)
            return None

        logger.info("successfully wrote a bad traffic record for {0}, orig id: {1}, dest_id: {2} at {3}".format(self.curr_date, orig_place_id, dest_place_id,curr_datetime))
        return True
    
    def write_traffic_resolved(self, orig_place_id: str, dest_place_id: str) -> bool:
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            qry = traffic_conditions.update().where(
                traffic_conditions.c.date == self.curr_date,
                traffic_conditions.c.origin_place_id == orig_place_id,
                traffic_conditions.c.dest_place_id == dest_place_id
                ).values(resolve_traffic_datetime=curr_datetime)

            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem writing traffic resolved record for orig id: {1}, dest_id: {2}".format(orig_place_id, dest_place_id))
            logger.error(e)
            return None
        
        logger.info("successfully wrote traffic resolved record for {0}, orig id: {1}, dest_id: {2} at {3}".format(self.curr_date, orig_place_id, dest_place_id,curr_datetime))
        return True