from traffic_man.google import MapGoogler
from traffic_man.config import Config
from traffic_man.twilio import TwilioSender
from time import sleep
from queue import Empty
import uuid


# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)



class TrafficEngine:
    msg_src = "traffic_engine"

    @staticmethod
    def _get_next_run(db_req_q, db_res_traffic_eng_q):
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "GET_SECONDS_TO_NEXT_RUN", "class-args": [], "method-args": []})
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
    def _get_orig_dest_pairs(db_req_q, db_res_traffic_eng_q) -> list:
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "GET_ORIG_DEST_PAIRS", "class-args": [], "method-args": []})
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
    def traffic_eng_worker(kill_q, db_req_q, db_res_traffic_eng_q):
        while kill_q.empty():
            sleep_seconds, flag_1201 = TrafficEngine._get_next_run(db_req_q, db_res_traffic_eng_q)
            if sleep_seconds == False:
                logger.error("problem getting seconds to sleep, setting to default of 60 sec")
                sleep_seconds = 60
                flag_1201 = True
            else:
                logger.info("seconds to sleep until next run: {0}".format(sleep_seconds))
                sleep(sleep_seconds/1000)

            if flag_1201:
                orig_dest_pairs = TrafficEngine._get_orig_dest_pairs(db_req_q, db_res_traffic_eng_q)
                map_googler = MapGoogler(orig_dest_pairs)
