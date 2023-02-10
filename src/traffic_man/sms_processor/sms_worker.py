from traffic_man.config import Config
from queue import Empty
from traffic_man.sms_processor.sms_messages import SMSMsg
from traffic_man.sms_processor.sms_data_manager import SMSDataMgr

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSWorker:

    @staticmethod
    def _sms_processor(sms_msg: object, db_req_q, db_res_sms_q) -> bool:
        if sms_msg.from_num_status == "invalid":
            if SMSDataMgr.log_sms_msg(sms_msg.from_num, sms_msg.sms_body, "invalid", "received", sms_msg.msg_rec_datetime , "inbound", db_req_q, db_res_sms_q):
                logger.info("logged invalid sms")
            else:
                logger.error("failed to log invalid sms")
        elif sms_msg.auto_status == "unsub":
            if SMSDataMgr.log_sms_msg(sms_msg.from_num, sms_msg.sms_body, "unsubscribe", "received", sms_msg.msg_rec_datetime , "inbound", db_req_q, db_res_sms_q):
                logger.info("logged unsubscribe sms")
            else:
                logger.error("failed to log unsubscribe sms")
            if not SMSDataMgr.get_user_by_phone_num(sms_msg.from_num, db_req_q, db_res_sms_q):
                if SMSDataMgr.set_user_by_phone_num(db_req_q, db_req_q, True, sms_msg.from_num, "unsub", "not auth"):
                    logger.info("successfully saved user as unsub")
                else:
                    logger.error("failed to save user as unsub")

    @staticmethod
    def sms_worker(kill_q, db_req_q, db_res_sms_q, inbound_sms_q):

        while kill_q.empty():
            try:
                inbound_sms = inbound_sms_q.get(timeout=3)
                sms_msg = SMSMsg(inbound_sms["Body"], inbound_sms["From"], inbound_sms["received_datetime"])            
                SMSWorker._sms_processor(sms_msg, db_req_q, db_res_sms_q)


            except Empty:
                logger.debug("sms inbound queue is empty")