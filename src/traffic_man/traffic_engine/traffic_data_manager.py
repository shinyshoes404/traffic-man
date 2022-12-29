from traffic_man.config import Config

from queue import Empty
import uuid


# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)



class TrafficDataMgr:
    msg_src = "traffic_engine"

    @staticmethod
    def get_next_run(db_req_q, db_res_traffic_eng_q):
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "GET_SECONDS_TO_NEXT_RUN", "class-args": [], "method-args": []})
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False, False
        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False, False
        return resp_msg.get("results")
    
    @staticmethod
    def get_orig_dest_pairs(db_req_q, db_res_traffic_eng_q) -> list:
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "GET_ORIG_DEST_PAIRS", "class-args": [], "method-args": []})
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False
        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        return resp_msg.get("results")

    @staticmethod
    def get_traffic_cond_data(db_req_q, db_res_traffic_eng_q):
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "CHECK_TRAFFIC_CONDITIONS", "class-args": [], "method-args":[]})
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False
        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        return resp_msg.get("results")

    @staticmethod
    def store_traffic_data(db_req_q, db_res_traffic_eng_q, traffic_data):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "STORE_TRAFFIC_DATA", "class-args": [], "method-args": [traffic_data]}
        try:
            db_req_q.put(msg)
        except Exception as e:
            logger.error("problem putting msg on the queue to store traffic data\n\tmsg: {0}".format(msg))
            logger.error(e)
            return False

        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False
        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        return resp_msg.get("results")

    @staticmethod
    def store_new_bad_traffic(db_req_q, db_res_traffic_eng_q, orig_place_id: str, dest_place_id: str):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "WRITE_BAD_TRAFFIC", "class-args": [], "method-args": [orig_place_id, dest_place_id]}
        try:
            db_req_q.put(msg)
        except Exception as e:
            logger.error("problem putting msg on the queue to store bad traffic records\n\tmsg: {0}".format(msg))
            logger.error(e)
            return False

        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")
    

    @staticmethod
    def store_resolved_traffic(db_req_q, db_res_traffic_eng_q, orig_place_id, dest_place_id):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "WRITE_TRAFFIC_RESOLVED", "class-args": [], "method-args": [orig_place_id, dest_place_id]}
        try:
            db_req_q.put(msg)
        except Exception as e:
            logger.error("problem putting msg on the queue to store resolved traffic records\n\tmsg: {0}".format(msg))
            logger.error(e)
            return False
            
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False
        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False
        return resp_msg.get("results")

    @staticmethod
    def get_phone_nums(db_req_q, db_res_traffic_eng_q, sms_type: str, orig_place_id: str, dest_place_id: str):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "GET_SMS_LIST_BY_TYPE", "class-args": [], "method-args": [sms_type, orig_place_id, dest_place_id]}
        try:
            db_req_q.put(msg)
        except Exception as e:
            logger.error("problem putting msg on the queue to get phone numbers \n\tmsg: {0}".format(msg))
            logger.error(e)
            return False
        
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")

    
    @staticmethod
    def store_sms_data(db_req_q, db_res_traffic_eng_q, sms_data: list):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficDataMgr.msg_src, "command": "WRITE_SMS_RECORDS", "class-args": [], "method-args": [sms_data]}
        try:
            db_req_q.put(msg)
        except Exception as e:
            logger.error("problem putting msg on the queue to store sms data\n\tmsg: {0}".format(msg))
            logger.error(e)
            return False
        
        try:
            resp_msg = db_res_traffic_eng_q.get(timeout=10)
        except Empty:
            logger.error("traffic engine response queue is empty and timed out")
            return False

        if resp_msg.get("msg-id") != msg_id:
            logger.error("the msg-id does not match")
            return False

        return resp_msg.get("results")


    @staticmethod
    def proc_bad_traffic_data(db_req_q, db_res_traffic_eng_q, bad_traffic_data: list) -> list:
        if bad_traffic_data is not None:
            # insert new bad traffic records into the db and get phone numbers to send sms to
            bad_traffic_phone_nums = []
            for record in bad_traffic_data:
                if TrafficDataMgr.store_new_bad_traffic(db_req_q, db_res_traffic_eng_q, record["orig_place_id"], record["dest_place_id"]):
                    temp_bad_traff_nums = TrafficDataMgr.get_phone_nums(db_req_q, db_res_traffic_eng_q, "bad traffic", record["orig_place_id"], record["dest_place_id"])
                    if temp_bad_traff_nums is not None and temp_bad_traff_nums is not False:
                        bad_traffic_phone_nums.extend(temp_bad_traff_nums)
            
            return bad_traffic_phone_nums
        
        else:
            return None        
    
    @staticmethod 
    def proc_resolved_traffic_data(db_req_q, db_res_traffic_eng_q, resolved_traffic_data: list) -> list:
        if resolved_traffic_data is not None:
            # insert resolved traffic records into the db and get phone numbers to send sms to
            resolved_traffic_phone_nums = []
            for record in resolved_traffic_data:
                if TrafficDataMgr.store_resolved_traffic(db_req_q, db_res_traffic_eng_q, record["orig_place_id"], record["dest_place_id"]):
                    temp_resolved_traff_nums = TrafficDataMgr.get_phone_nums(db_req_q, db_res_traffic_eng_q, "traffic resolved", record["orig_place_id"], record["dest_place_id"])
                    if temp_resolved_traff_nums is not None and temp_resolved_traff_nums is not False:
                        resolved_traffic_phone_nums.extend(temp_resolved_traff_nums)
            return resolved_traffic_phone_nums
        
        else:
            return None