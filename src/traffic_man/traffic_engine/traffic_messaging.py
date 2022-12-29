from traffic_man.twilio.twilio import TwilioSender
from traffic_man.traffic_engine.traffic_data_manager import TrafficDataMgr

from traffic_man.config import Config

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class TrafficMessenger:
    
    @staticmethod
    def send_bad_traffic_sms(db_req_q, db_res_traffic_eng_q, phone_nums: list) -> int:
        ts = TwilioSender()
        results = ts.send_bad_traffic_sms(phone_nums)
        if results:
            store_result = TrafficDataMgr.store_sms_data(db_req_q, db_res_traffic_eng_q, results)
            return store_result
        return None
    
    @staticmethod
    def send_resolved_traffic_sms(db_req_q, db_res_traffic_eng_q, phone_nums: list) -> int:
        ts = TwilioSender()
        results = ts.send_resolved_traffic_sms(phone_nums)
        if results:
            store_result = TrafficDataMgr.store_sms_data(db_req_q, db_res_traffic_eng_q, results)
            return store_result
        return None
