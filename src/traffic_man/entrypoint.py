from traffic_man.config import Config
from traffic_man.db.db_worker import db_worker
from traffic_man.traffic_engine.traffic_eng_worker import TrafficEngine

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
    kill_q = Queue()

    db_worker_thread = threading.Thread(target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q])
    traffic_eng_worker_thread = threading.Thread(target=TrafficEngine.traffic_eng_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q])
    
    db_worker_thread.start()
    traffic_eng_worker_thread.start()

    try:
        while True:
            sleep(5)
            print("traffic man is running")
    except KeyboardInterrupt:
        kill_q.put("kill")
        kill_q.put("kill")
        kill_q.put("kill")
        print("shutting down traffic man")
    
    db_worker_thread.join()
    traffic_eng_worker_thread.join()


if __name__ == "__main__":
    main()

