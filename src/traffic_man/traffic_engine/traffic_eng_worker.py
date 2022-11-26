from traffic_man.google.map_googler import MapGoogler
from traffic_man.google.orig_dest_optimizer import OrigDestOptimizer
from traffic_man.traffic_engine.traffic_data_processor import TrafficDataProc
from traffic_man.db.sms_data import SMSData
from traffic_man.config import Config
from traffic_man.twilio.twilio import TwilioSender
from time import sleep
from queue import Empty
import uuid
from datetime import datetime, timedelta


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
    def _get_traffic_cond_data(db_req_q, db_res_traffic_eng_q):
        msg_id = str(uuid.uuid4())
        db_req_q.put({"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "CHECK_TRAFFIC_CONDITIONS", "class-args": [], "method-args":[]})
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
    def _store_traffic_data(db_req_q, db_res_traffic_eng_q, traffic_data):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "STORE_TRAFFIC_DATA", "class-args": [], "method-args": [traffic_data]}
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
    def _store_new_bad_traffic(db_req_q, db_res_traffic_eng_q, orig_place_id: str, dest_place_id: str):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "WRITE_BAD_TRAFFIC", "class-args": [], "method-args": [orig_place_id, dest_place_id]}
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
    def _store_resolved_traffic(db_req_q, db_res_traffic_eng_q, orig_place_id, dest_place_id):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "WRITE_TRAFFIC_RESOLVED", "class-args": [], "method-args": [orig_place_id, dest_place_id]}
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
    def _get_phone_nums(db_req_q, db_res_traffic_eng_q, sms_type: str, orig_place_id: str, dest_place_id: str):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "GET_SMS_LIST_BY_TYPE", "class-args": [], "method-args": [sms_type, orig_place_id, dest_place_id]}
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
    def _sleep_routine(kill_q, sleep_seconds) -> bool:
        done_time = datetime.now() + timedelta(seconds=sleep_seconds)
        while kill_q.empty() and datetime.now() < done_time:
            sleep(5)
        
        if not kill_q.empty():
            logger.warning("exiting sleep routine because kill queue is not empty")
            return False
        else:
            return True
    
    @staticmethod
    def _store_sms_data(db_req_q, db_res_traffic_eng_q, sms_data: list):
        msg_id = str(uuid.uuid4())

        msg = {"msg-id": msg_id, "msg-src": TrafficEngine.msg_src, "command": "WRITE_SMS_RECORDS", "class-args": [], "method-args": [sms_data]}
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
    def _send_bad_traffic_sms(db_req_q, db_res_traffic_eng_q, phone_nums: list) -> int:
        ts = TwilioSender()
        results = ts.send_bad_traffic_sms(phone_nums)
        if results:
            store_result = TrafficEngine._store_sms_data(db_req_q, db_res_traffic_eng_q, results)
            return store_result
        return None
    
    @staticmethod
    def _send_resolved_traffic_sms(db_req_q, db_res_traffic_eng_q, phone_nums: list) -> int:
        ts = TwilioSender()
        results = ts.send_resolved_traffic_sms(phone_nums)
        if results:
            store_result = TrafficEngine._store_sms_data(db_req_q, db_res_traffic_eng_q, results)
            return store_result
        return None

    @staticmethod
    def _proc_traffic_conditions(db_req_q, db_res_traffic_eng_q, traffic_data_proc_obj: object):
        # only proceed if we don't have issues building out the the data frames in pandas
        if traffic_data_proc_obj.build_dfs():
            new_bad_traffic = traffic_data_proc_obj.get_new_bad_traffic()
            resolved_traffic = traffic_data_proc_obj.get_resolved_traffic()

            bad_traffic_phone_nums = TrafficEngine._proc_bad_traffic_data(db_req_q, db_res_traffic_eng_q, new_bad_traffic)
            resolved_traffic_phone_nums = TrafficEngine._proc_resolved_traffic_data(db_req_q, db_res_traffic_eng_q, resolved_traffic)
            
            return bad_traffic_phone_nums, resolved_traffic_phone_nums

        else:
            return None, None

    @staticmethod
    def _proc_bad_traffic_data(db_req_q, db_res_traffic_eng_q, bad_traffic_data: list) -> list:
        if bad_traffic_data is not None:
            # insert new bad traffic records into the db and get phone numbers to send sms to
            bad_traffic_phone_nums = []
            for record in bad_traffic_data:
                if TrafficEngine._store_new_bad_traffic(db_req_q, db_res_traffic_eng_q, record["orig_place_id"], record["dest_place_id"]):
                    temp_bad_traff_nums = TrafficEngine._get_phone_nums(db_req_q, db_res_traffic_eng_q, "bad traffic", record["orig_place_id"], record["dest_place_id"])
                    if temp_bad_traff_nums is not None and temp_bad_traff_nums is not False:
                        bad_traffic_phone_nums.extend(temp_bad_traff_nums)
            
            return bad_traffic_phone_nums
        
        else:
            return None        
    
    @staticmethod 
    def _proc_resolved_traffic_data(db_req_q, db_res_traffic_eng_q, resolved_traffic_data: list) -> list:
        if resolved_traffic_data is not None:
            # insert resolved traffic records into the db and get phone numbers to send sms to
            resolved_traffic_phone_nums = []
            for record in resolved_traffic_data:
                if TrafficEngine._store_resolved_traffic(db_req_q, db_res_traffic_eng_q, record["orig_place_id"], record["dest_place_id"]):
                    temp_resolved_traff_nums = TrafficEngine._get_phone_nums(db_req_q, db_res_traffic_eng_q, "traffic resolved", record["orig_place_id"], record["dest_place_id"])
                    if temp_resolved_traff_nums is not None and temp_resolved_traff_nums is not False:
                        resolved_traffic_phone_nums.extend(temp_resolved_traff_nums)
            return resolved_traffic_phone_nums
        
        else:
            return None


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
                if not TrafficEngine._sleep_routine(kill_q, sleep_seconds):
                    break

            if not flag_1201:

                # get orig dest pairs from the db
                orig_dest_pairs = TrafficEngine._get_orig_dest_pairs(db_req_q, db_res_traffic_eng_q)
                if orig_dest_pairs: # if we encounter an exception (False) or no orig dest pairs (None), don't proceed

                    # get traffic conditions from db - reuse for each google call
                    traffic_cond_data = TrafficEngine._get_traffic_cond_data(db_req_q, db_res_traffic_eng_q)
                    logger.debug("traffic conditions:\n{0}".format(traffic_cond_data))

                    # only proceed if we didn't run into an exception (False) when getting the traffic condition data,
                    #  getting back {} from the db is valid, because there may not be any traffic condition recorded yet for the day
                    if traffic_cond_data is not False:

                        # optimize the orig dest pairs for the Google maps api to limit the number of API calls we have to make without exceeding the limits enforced by the api
                        odp = OrigDestOptimizer(orig_dest_pairs)
                        optimized_orig_dest_list = odp.get_orig_dest_list()
                        logger.debug("optimized orig dest list:\n{0}".format(optimized_orig_dest_list))

                        if optimized_orig_dest_list:
                            # loop through our optimized origin dest list, call google, and calculate results
                            for orig_dest_set in optimized_orig_dest_list:
                                logger.debug("orig dest set:\n{0}".format(orig_dest_set))
                                
                                orig_list, dest_list = MapGoogler.build_orig_dest_lists(orig_dest_set)
                                logger.debug("orig list:\n{0}".format(orig_list))
                                logger.debug("dest list:\n{0}".format(dest_list))

                                # get traffic data from Google maps api
                                mg = MapGoogler(orig_list, dest_list)
                                google_maps_raw = mg.google_call_with_retry(3)
                                
                                # only proceed if we successfully fetched results
                                if google_maps_raw: 
                                    # calculate and restructure google data
                                    struct_google_data = MapGoogler.calc_traffic(google_maps_raw, orig_dest_set)
                                    logger.debug("structured google data:\n{0}".format(struct_google_data))

                                    # only proceed if we were able to successfully restructure the data and calculate the traffic ratio
                                    if struct_google_data:

                                        # store the google traffic data in the db
                                        for data in struct_google_data:
                                            TrafficEngine._store_traffic_data(db_req_q, db_res_traffic_eng_q, data)


                                        # determine with orig dest pairs that need to traffic conditions updated (traffic is bad, traffic is resolved) and sms messages sent
                                        tdp = TrafficDataProc(struct_google_data, traffic_cond_data)
                                        bad_traff_phone_nums, resolved_traff_phone_nums = TrafficEngine._proc_traffic_conditions(db_req_q, db_res_traffic_eng_q, tdp)
                                        logger.debug("bad traffic phone nums:\n{0}".format(bad_traff_phone_nums))
                                        logger.debug("resolved traffic phone nums:\n{0}".format(resolved_traff_phone_nums))

                                        # send our sms messages and store a record of what we sent in the database
                                        if bad_traff_phone_nums is not None:
                                            TrafficEngine._send_bad_traffic_sms(db_req_q, db_res_traffic_eng_q, bad_traff_phone_nums)
                                        if resolved_traff_phone_nums is not None:
                                            TrafficEngine._send_resolved_traffic_sms(db_req_q, db_res_traffic_eng_q, resolved_traff_phone_nums)