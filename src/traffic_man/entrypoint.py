from traffic_man.db_ops import DataSetup, TrafficDateTime, TrafficData, SMSData
from traffic_man.google import MapGoogler
from traffic_man.config import Config
from traffic_man.twilio import TwilioSender
from time import sleep
import logging

import sqlalchemy as db
from traffic_man.config import Config
from traffic_man.models import metadata_obj

engine = db.create_engine('sqlite:///' + Config.db_path)
metadata_obj.create_all(engine)

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

# need for unit testing
def keep_running():
    return True

def main():
    # db setup - If any of these steps are not successful return, do not move forward
    logger.info("setting up the database")

    data_setup = DataSetup(engine)
    if not data_setup.update_check_times():
        return None
    if not data_setup.update_holidays():
        return None
    if not data_setup.update_check_days():
        return None
    if not data_setup.update_phone_numbers():
        return None

    logger.info("database setup complete")

    # implementing keep_running, just for unit testing
    while keep_running():
        traffic_date = TrafficDateTime(engine)

        sleep_seconds, flag_1201 = traffic_date.get_next_run_sleep_seconds()
        logger.info("seconds to sleep until next run: {0}".format(sleep_seconds))
        sleep(sleep_seconds)

        # only run through the rest of the routine (including API calls that cost money) if we weren't just sleeping until 12:01 AM the following day
        if not flag_1201:

            map_googler = MapGoogler()
            raw_maps_data = map_googler.google_call_with_retry(3)
        
            # only move forward if we were able to get google maps data
            if raw_maps_data:
            
                maps_data_tranformed = MapGoogler.calc_traffic(raw_maps_data)
                # only move forward if the raw data was successfully transformed
                if maps_data_tranformed:
                    traffic_data = TrafficData(engine)
                    traffic_data.store_traffic_data(maps_data_tranformed)

                    if maps_data_tranformed["traffic_ratio"] >= Config.overage_parameter:        
                        traffic_condition = traffic_data.check_traffic_conditions()
                        if traffic_condition == None:
                            traffic_data.write_bad_traffic()                        
                            # don't send more than one bad traffic sms per day
                            sms_data = SMSData(engine)                        
                            if sms_data.check_sms_today("bad traffic") == False:  
                                twilio_sender = TwilioSender()                   
                                err_count = twilio_sender.send_bad_traffic_sms(traffic_data.get_phone_numbers())
                                sms_data.write_sms_record("bad traffic", err_count)
                    
                    elif maps_data_tranformed["traffic_ratio"] < (Config.overage_parameter * 0.5):
                        traffic_condition = traffic_data.check_traffic_conditions()
                        if traffic_condition == "traffic":
                            traffic_data.write_traffic_resolved()
                            # don't send more than one traffic resolved sms per day
                            sms_data = SMSData(engine)
                            if sms_data.check_sms_today("traffic resolved") == False:
                                twilio_sender = TwilioSender()
                                err_count = twilio_sender.send_resolved_traffic_sms(traffic_data.get_phone_numbers())
                                sms_data.write_sms_record("traffic resolved", err_count)