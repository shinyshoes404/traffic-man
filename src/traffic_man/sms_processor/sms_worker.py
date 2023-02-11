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
    def _sms_log_and_user_update(msg_typ: str, sms_msg, db_req_q, db_res_sms_q) -> None:
        # log the received sms
        if SMSDataMgr.log_sms_msg(sms_msg.from_num, sms_msg.sms_body, msg_typ, "received", sms_msg.msg_rec_datetime , "inbound", db_req_q, db_res_sms_q):
            logger.info("logged {0} sms".format(msg_typ))
        else:
            logger.error("failed to log {0}} sms".format(msg_typ))


    @staticmethod
    def _auto_sms_set_user(status: str, sms_msg, db_req_q, db_res_sms_q) -> None:
        # create or update user
        user_data = SMSDataMgr.get_user_by_phone_num(sms_msg.from_num, db_req_q, db_res_sms_q)
        if not user_data:
            if SMSDataMgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, sms_msg.from_num, status, "not auth"):
                logger.info("successfully created user with {0}} status".format(status))
            else:
                logger.error("failed to create user with {0}} status".format(status))
        else:
            if SMSDataMgr.set_user_by_phone_num(db_req_q, db_res_sms_q, False, sms_msg.from_num, status):
                logger.info("successfully updated user with {0}} status".format(status))
            else:
                logger.error("failed to update user with {0}} status".format(status))


    @staticmethod
    def _auto_sms_processor(sms_msg: object, db_req_q, db_res_sms_q) -> bool:
        # log invalid phone numbers to make sure watch dog can keep track of them
        if sms_msg.from_num_status == "invalid":
            if SMSWorker._sms_log_and_user_update("invalid", sms_msg, db_req_q, db_res_sms_q):
                logger.info("logged invalid sms")
            else:
                logger.error("failed to log invalid sms")                            
            return True
        
        # manage automated response scenarios
        if sms_msg.auto_status == "unsub":
            SMSWorker._sms_log_and_user_update("unsubscribe", sms_msg, db_req_q, db_res_sms_q)
            SMSWorker._auto_sms_set_user("unsub", sms_msg, db_req_q, db_res_sms_q)
            return True

        if sms_msg.auto_status == "sub":
            SMSWorker._sms_log_and_user_update("subscribe", sms_msg, db_req_q, db_res_sms_q)
            SMSWorker._auto_sms_set_user("sub", sms_msg, db_req_q, db_res_sms_q)
            return True

        if sms_msg.auto_status == "help":
            SMSWorker._sms_log_and_user_update("info", sms_msg, db_req_q, db_res_sms_q)
            return True
        
        return False


    @staticmethod
    def sms_worker(kill_q, db_req_q, db_res_sms_q, inbound_sms_q):

        while kill_q.empty():
            try:
                inbound_sms = inbound_sms_q.get(timeout=3)
            except Empty:
                logger.debug("sms inbound queue is empty")
            
            sms_msg = SMSMsg(inbound_sms["Body"], inbound_sms["From"], inbound_sms["received_datetime"]) 

            if not SMSWorker._auto_sms_processor(sms_msg, db_req_q, db_res_sms_q):
                # if this isn't an auto scenario, continue processing the sms message
                pass