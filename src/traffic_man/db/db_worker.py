import sqlalchemy as db
from queue import Empty

from traffic_man.config import Config
from traffic_man.db.db_ops_mapping import db_ops_mapping
from traffic_man.db.data_setup import DataSetup
from traffic_man.db.models import metadata_obj

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

def db_worker(kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q):
    engine = db.create_engine('sqlite:///' + Config.db_path)
    metadata_obj.create_all(engine)
    
    # db setup - If any of these steps are not successful return, do not move forward
    logger.info("setting up the database")

    data_setup = DataSetup(engine)
    if not data_setup.update_check_times():
        return None
    if not data_setup.update_holidays():
        return None
    if not data_setup.update_check_days():
        return None
    
    logger.info("database setup complete")

    while kill_q.empty():
        try:
            qry_req_msg = db_req_q.get(timeout=3)
            msg_id = qry_req_msg.get("msg-id")
            if msg_id == None:
                logger.error("missing msg-id")
            msg_src = qry_req_msg.get("msg-src")
            if msg_src == None:
                logger.error("missing msg-src")
            db_ops_map_obj = db_ops_mapping.get(qry_req_msg.get("command"))
            db_obj_instance = db_ops_map_obj.get("class")(engine, *qry_req_msg.get("class-args"))
            db_op_result = db_ops_map_obj.get("method")(db_obj_instance, *qry_req_msg.get("method-args"))
            if msg_src == "traffic_engine":
                db_res_traffic_eng_q.put({"msg-id": msg_id, "msg_src": msg_src, "results": db_op_result})
            if msg_src == "sms_processor":
                db_res_sms_q.put({"msg-id": msg_id, "msg_src": msg_src, "results": db_op_result})
        except Empty:
            logger.debug("db request queue is empty")