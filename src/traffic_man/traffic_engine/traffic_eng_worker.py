from traffic_man.google.map_googler import MapGoogler
from traffic_man.google.orig_dest_optimizer import OrigDestOptimizer
from traffic_man.traffic_engine.traffic_data_processor import TrafficDataProc
from traffic_man.traffic_engine.traffic_data_manager import TrafficDataMgr
from traffic_man.traffic_engine.traffic_messaging import TrafficMessenger
from traffic_man.config import Config

from time import sleep
from datetime import datetime, timedelta


# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)



class TrafficEngine:

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
    def traffic_eng_worker(kill_q, db_req_q, db_res_traffic_eng_q):
        while kill_q.empty():
            sleep_seconds, flag_1201 = TrafficDataMgr.get_next_run(db_req_q, db_res_traffic_eng_q)
            if sleep_seconds == False:
                logger.error("problem getting seconds to sleep, setting to default of 60 sec")
                sleep_seconds = 60
                flag_1201 = True
                
            logger.info("seconds to sleep until next run: {0}".format(sleep_seconds))
            if not TrafficEngine._sleep_routine(kill_q, sleep_seconds):
                break

            if not flag_1201:

                # get orig dest pairs from the db
                orig_dest_pairs = TrafficDataMgr.get_orig_dest_pairs(db_req_q, db_res_traffic_eng_q)
                if orig_dest_pairs: # if we encounter an exception (False) or no orig dest pairs (None), don't proceed

                    # get traffic conditions from db - reuse for each google call
                    traffic_cond_data = TrafficDataMgr.get_traffic_cond_data(db_req_q, db_res_traffic_eng_q)
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
                                            TrafficDataMgr.store_traffic_data(db_req_q, db_res_traffic_eng_q, data)


                                        # determine with orig dest pairs that need to traffic conditions updated (traffic is bad, traffic is resolved) and sms messages sent
                                        tdp = TrafficDataProc(struct_google_data, traffic_cond_data)
                                        # only proceed if we can successfully create our data frames
                                        if tdp.build_dfs():
                                            new_bad_traffic = tdp.get_new_bad_traffic()
                                            resolved_traffic = tdp.get_resolved_traffic()

                                            bad_traffic_phone_nums = TrafficDataMgr.proc_bad_traffic_data(db_req_q, db_res_traffic_eng_q, new_bad_traffic)
                                            resolved_traffic_phone_nums = TrafficDataMgr.proc_resolved_traffic_data(db_req_q, db_res_traffic_eng_q, resolved_traffic)
                                        
                                            logger.debug("bad traffic phone nums:\n{0}".format(bad_traffic_phone_nums))
                                            logger.debug("resolved traffic phone nums:\n{0}".format(resolved_traffic_phone_nums))

                                            # send our sms messages and store a record of what we sent in the database
                                            if bad_traffic_phone_nums is not None:
                                                TrafficMessenger.send_bad_traffic_sms(db_req_q, db_res_traffic_eng_q, bad_traffic_phone_nums)
                                            if resolved_traffic_phone_nums is not None:
                                                TrafficMessenger.send_resolved_traffic_sms(db_req_q, db_res_traffic_eng_q, resolved_traffic_phone_nums)