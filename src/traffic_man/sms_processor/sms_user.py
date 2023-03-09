from traffic_man.config import Config
from traffic_man.sms_processor.sms_data_manager import SMSDataMgr
from queue import Queue

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSUser:
    def __init__(self, phone_num: str, db_req_q: Queue, db_res_sms_q: Queue):
        self.phone_num = phone_num
        self.db_req_q = db_req_q
        self.db_res_sms_q = db_res_sms_q
        self._build_user()
        self.new_auth = False

    def _build_user(self) -> None:
        get_user_result = SMSDataMgr.get_user_by_phone_num(self.phone_num, self.db_req_q, self.db_res_sms_q)
        if get_user_result is False:
            self.user_error = True
        else:
            self.user_error = False
        
            if get_user_result:
                self.new_user = False
                self.origin_place_id = get_user_result["origin_place_id"]
                self.dest_place_id = get_user_result["dest_place_id"]
                self.status = get_user_result["status"]
                self.auth_status = get_user_result["auth_status"]
                              
            else:
                self.new_user = True
                self.origin_place_id = None
                self.dest_place_id = None
                self.status = "needs setup"
                self.auth_status = "not auth"

