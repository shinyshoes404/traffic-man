import uuid
from traffic_man.config import Config
from queue import Empty, Queue

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class SMSDataMgr:
    msg_src = "sms_processor"

    @staticmethod
    def log_sms_msg(from_num: str, sms_msg: str, sms_type: str, sms_status: str, msg_datetime: str, sms_direction: str, db_req_q, db_res_sms_q):
        msg_id = str(uuid.uuid4())
        sms_data = [{"datetime": msg_datetime, "sms_type": sms_type, "status": sms_status, "direction": sms_direction, "msg_content": sms_msg, "phone_num": from_num}]
        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "WRITE_SMS_RECORDS", "class-args": [], "method-args": [sms_data]}

        logger.debug("log sms PUT {0}".format(msg))

        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("log sms - sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        
        logger.debug("log sms - RESULT - {0}".format(resp_msg))
        return resp_msg.get("results")
    
    @staticmethod
    def get_user_by_phone_num(phone_num: str, db_req_q: Queue, db_res_sms_q: Queue):
        msg_id = str(uuid.uuid4())
        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "GET_USER_BY_PHONE_NUM", "class-args": [], "method-args": [phone_num]}

        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("get user - sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")

    @staticmethod
    def set_user_by_phone_num(db_req_q: Queue, db_res_sms_q: Queue, sms_user):
        msg_id = str(uuid.uuid4())

        user_data = {
            "phone_num": sms_user.phone_num, 
            "status": sms_user.status,
            "auth_status": sms_user.auth_status,
            "origin_place_id": sms_user.origin_place_id,
            "dest_place_id": sms_user.dest_place_id,
            "origin_place_id_confirmed": sms_user.origin_place_id_confirmed,
            "dest_place_id_confirmed": sms_user.dest_place_id_confirmed
            }

        msg = {"msg-id": msg_id, "msg-src": SMSDataMgr.msg_src, "command": "SET_USER_BY_PHONE_NUM", "class-args": [], "method-args": [user_data, sms_user.new_user]}

        logger.debug("sms data mgr - PUT - {0}".format(msg))
        db_req_q.put(msg)
        try:
            resp_msg = db_res_sms_q.get(timeout=10)
        except Empty:
            logger.error("set user - sms processor response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        logger.debug("data mgr response: {0}".format(resp_msg))
        return resp_msg.get("results")
