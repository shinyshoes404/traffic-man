from traffic_man.db.models import sms_data, phone_numbers 
from traffic_man.config import Config
from datetime import datetime
from sqlalchemy import join, select, outerjoin

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
    
    def get_phone_nums(self, sms_type: str, orig_place_id: str, dest_place_id: str) -> list:
        

        try:
            phone_num_subqry = phone_numbers.select(phone_numbers.c.phone_num
                                ).where(phone_numbers.c.origin_place_id == orig_place_id,
                                        phone_numbers.c.dest_place_id == dest_place_id,
                                        phone_numbers.c.status == "sub",
                                        phone_numbers.c.auth_status == "auth").subquery()
            
            sms_sent_subqry = sms_data.select(sms_data.c.phone_num
                                        ).where(sms_data.c.datetime >= self.curr_date,
                                                sms_data.c.sms_type == sms_type,
                                                sms_data.c.status == "sent",
                                                sms_data.c.direction == "outbound").subquery()
            
            outer_join_subqry = outerjoin(phone_num_subqry, sms_sent_subqry, phone_num_subqry.c.phone_num == sms_sent_subqry.c.phone_num)

            qry = select([phone_num_subqry.c.phone_num]).select_from(outer_join_subqry).filter(sms_sent_subqry.c.phone_num == None)


        
            with self.engine.connect() as connection:
                result_obj = connection.execute(qry)
                results_data = result_obj.fetchall()
        except Exception as e:
            logger.error("problem getting sms records for origin: {0}  dest: {1}".format(orig_place_id, dest_place_id))
            logger.error(e)
            return None
        
        if len(results_data) == 0:
            logger.info("{0} sms message already sent for origin: {1}  dest: {2}".format(sms_type, orig_place_id, dest_place_id))
            return []
        
        logger.info("{0} phone numbers need a {1} sms sent to them".format(len(results_data), sms_type))
        phone_num_list = []
        for row in results_data:
            phone_num_list.append(row[0])
        
        return phone_num_list
        

    def write_sms_records(self, sms_data_list: list) -> int:
        logger.info("attempting to add {0} sms records for {1}".format(len(sms_data_list), self.curr_date))
        error_count = 0
        # inserting one at a time so one bad record doesn't prevent the rest from being written to the db
        for record in sms_data_list:
            try:
                qry = sms_data.insert().values(record)
                with self.engine.connect() as connection:
                    connection.execute(qry)
            except Exception as e:
                logger.error("problem inserting sms record \n{0}".format(record))
                logger.error(e)
                error_count += 1
        logger.info("error count while writing sms records: {0}".format(error_count))
        
        return error_count