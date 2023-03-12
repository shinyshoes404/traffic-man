banner = """
  ##############################################################################################

                #####   #######     #     ######   #######  ###  #     #   #####  
               #           #      #   #   #     #     #      #   # #   #  #       
                #####      #     #     #  ######      #      #   #  #  #  #  #### 
                     #     #     #######  #   #       #      #   #   # #  #     # 
                #####      #     #     #  #     #     #     ###  #     #   #####
 
   #######  ######      #     #######  #######  ###   #####       #     #     #     #     # 
      #     #     #   #   #   #        #         #   #            # # # #   #   #   # #   # 
      #     ######   #     #  #####    #####     #   #            #  #  #  #     #  #  #  # 
      #     #   #    #######  #        #         #   #            #     #  #######  #   # # 
      #     #     #  #     #  #        #        ###   #####       #     #  #     #  #     #

###############################################################################################


"""
print(banner)

from traffic_man.config import Config
from traffic_man.db.db_worker import db_worker
from traffic_man.traffic_engine.traffic_eng_worker import TrafficEngine
from traffic_man.sms_processor.sms_listener import SMSListener
from traffic_man.sms_processor.sms_worker import SMSWorker
import redis

from time import sleep
import threading
from queue import Queue

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

def main():
    db_req_q = Queue()
    db_res_traffic_eng_q = Queue()
    inbound_sms_q = Queue()
    db_res_sms_q = Queue()
    kill_q = Queue()

    db_worker_thread = threading.Thread(target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
    traffic_eng_worker_thread = threading.Thread(target=TrafficEngine.traffic_eng_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q])
    
    # redis listener thread
    redis_conn = redis.Redis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db, password=Config.redis_pw, decode_responses=True)
    sms_listener_thread = threading.Thread(target=SMSListener.get_message, args=[redis_conn, Config.redis_sms_stream_key, Config.redis_sms_consum_grp, "sms-listener-01", Config.redis_msg_read_count, Config.redis_block_time_ms, inbound_sms_q, kill_q])
    
    sms_proc_thread = threading.Thread(target=SMSWorker.sms_worker, args=[kill_q, db_req_q, db_res_sms_q, inbound_sms_q])


    db_worker_thread.start()
    traffic_eng_worker_thread.start()
    sms_listener_thread.start()
    sms_proc_thread.start()

    try:
        while True:
            sleep(5)
            print("traffic man is running")
    except KeyboardInterrupt:
        for i in range (0,10):
            kill_q.put("kill")
        logger.warning("shutting down traffic man")
    
    db_worker_thread.join()
    traffic_eng_worker_thread.join()
    sms_listener_thread.join()
    sms_proc_thread.join()


if __name__ == "__main__":
    main()

