import uuid
from traffic_man.config import Config
from queue import Empty

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class SMSDataMgr:
    msg_src = "sms_processor"

    @staticmethod
    def log_sms_msg(from_num: str, sms_msg: str, sms_type: str, sms_status: str, msg_rec_datetime: str, sms_direction: str, db_req_q, db_res_sms_q):
        msg_id = str(uuid.uuid4())
        sms_data = [{"datetime": msg_rec_datetime, "sms_type": sms_type, "status": sms_status, "direction": sms_direction, "msg_content": sms_msg, "phone_num": from_num}]
        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "WRITE_SMS_RECORDS", "class-args": [], "method-args": [sms_data]}

        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")
    
    @staticmethod
    def get_user_by_phone_num(phone_num: str, db_req_q, db_res_sms_q):
        msg_id = str(uuid.uuid4())
        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "GET_USER_BY_PHONE_NUM", "class-args": [], "method-args": [phone_num]}

        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")

    @staticmethod
    def set_user_by_phone_num(db_req_q, db_res_sms_q, new_flag: bool, phone_num: str, status: str = None, auth_status: str = None, origin_place_id: str = None, dest_place_id: str = None):
        msg_id = str(uuid.uuid4())

        user_data = {"phone_num": phone_num}
        
        if new_flag:
            user_data["status"] = status
            user_data["auth_status"] = auth_status
            user_data["origin_place_id"] = origin_place_id
            user_data["dest_place_id"] = dest_place_id
        
        else:
            if status:
                user_data["status"] = status
            if auth_status:
                user_data["auth_status"] = auth_status
            if origin_place_id:
                user_data["origin_place_id"] = origin_place_id
            if dest_place_id:
                user_data["dest_place_id"] = dest_place_id

        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "SET_USER_BY_PHONE_NUM", "class-args": [], "method-args": [user_data, new_flag]}

        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")
