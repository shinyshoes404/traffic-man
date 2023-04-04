from traffic_man.config import Config
from queue import Empty, Queue
from traffic_man.sms_processor.sms_messages import SMSMsg
from traffic_man.sms_processor.sms_user import SMSUser
from traffic_man.sms_processor.sms_data_manager import SMSDataMgr
from traffic_man.twilio.twilio import TwilioSender
from traffic_man.google.map_googler import PlaceFinder
import os, datetime

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSWorker:

    @staticmethod
    def _sms_log(msg_typ: str, sms_msg: SMSMsg, db_req_q: Queue, db_res_sms_q: Queue) -> bool:
        # log the received sms (log_sms_msg returns error count)
        if SMSDataMgr.log_sms_msg(sms_msg.from_num, sms_msg.sms_body, msg_typ, "received", sms_msg.msg_rec_datetime , "inbound", db_req_q, db_res_sms_q) == 0:
            logger.info("logged {0} sms".format(msg_typ))
            return True
        else:
            logger.error("failed to log {0} sms".format(msg_typ))
            return False


    @staticmethod
    def _send_need_auth(ts: TwilioSender, phone_num: str, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_need_auth_sms(phone_num)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"        
        SMSDataMgr.log_sms_msg(phone_num, sms_body, "auth needed", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _send_sub_sms(ts: TwilioSender, phone_num: str, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_sub_sms(phone_num)
        
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        
        SMSDataMgr.log_sms_msg(phone_num, sms_body, "subscribe", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _send_auth_success(ts: TwilioSender, phone_num: str, db_req_q: Queue, db_res_sms_q: Queue) -> None:        
        sent_status, sms_body = ts.send_auth_success_sms(phone_num)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"        
        SMSDataMgr.log_sms_msg(phone_num, sms_body, "auth success", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _send_service_error_sms(ts: TwilioSender, phone_num: str, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_service_error_sms(phone_num)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        SMSDataMgr.log_sms_msg(phone_num, sms_body, "service error", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _send_needs_setup_sms(ts: TwilioSender, sms_user: SMSUser, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_needs_setup_sms(sms_user)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        SMSDataMgr.log_sms_msg(sms_user.phone_num, sms_body, "needs setup", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _send_user_info_sms(ts: TwilioSender, sms_user: SMSUser, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_user_info_sms(sms_user)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        SMSDataMgr.log_sms_msg(sms_user.phone_num, sms_body, "info", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)

    @staticmethod
    def _send_addr_check(ts: TwilioSender, sms_user: SMSUser, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_addr_check(sms_user)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        SMSDataMgr.log_sms_msg(sms_user.phone_num, sms_body, "addr check", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)

    @staticmethod
    def _send_no_results(ts: TwilioSender, sms_user: SMSUser, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        sent_status, sms_body = ts.send_no_results_sms(sms_user)
        if sent_status:
            sms_status = "sent"
        else:
            sms_status = "failed"
        SMSDataMgr.log_sms_msg(sms_user.phone_num, sms_body, "no results", sms_status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "outbound", db_req_q, db_res_sms_q)


    @staticmethod
    def _check_auth(sms_msg: SMSMsg) -> bool:
        if sms_msg.sms_body.replace(" ", "").lower() == os.environ["TRAFFIC_MAN_CODE"].replace(" ", "").lower():
            logger.info("pass phrase matches")
            return True
                
        return False
    
    
    @staticmethod
    def _set_user(sms_user: SMSUser, db_req_q: Queue, db_res_sms_q: Queue) -> None:        
        if sms_user.new_user:
            if SMSDataMgr.set_user_by_phone_num(db_req_q, db_res_sms_q, sms_user):
                logger.info("created user with these characteristics | phone number: {0}| status: {1} | auth status: {2}".format(sms_user.phone_num, sms_user.status, sms_user.auth_status))                                    
            else:
                logger.error("failed to create user for phone number: {0}".format(sms_user.phone_num))
                sms_user.user_error = True           
        else:
            if SMSDataMgr.set_user_by_phone_num(db_req_q, db_res_sms_q, sms_user):
                logger.info("updated user with these characteristics | phone number: {0}| status: {1} | auth status: {2} | origin_place_id: {3} | origin id conf: {4} | dest_place_id: {5} | dest conf: {6}".format(
                    sms_user.phone_num, sms_user.status, sms_user.auth_status, sms_user.origin_place_id, sms_user.origin_place_id_confirmed, sms_user.dest_place_id, sms_user.dest_place_id_confirmed))                                    
            else:
                logger.error("failed to updated user for phone number: {0}".format(sms_user.phone_num))
                sms_user.user_error = True


    @staticmethod
    def _log_inbound_sms(sms_msg: SMSMsg, db_req_q: Queue, db_res_sms_q: Queue) -> None:

        if sms_msg.auto_status == "unsub":
            SMSWorker._sms_log("unsubscribe", sms_msg, db_req_q, db_res_sms_q)

        elif sms_msg.auto_status == "sub":
            SMSWorker._sms_log("subscribe", sms_msg, db_req_q, db_res_sms_q)

        elif sms_msg.auto_status == "info":
            SMSWorker._sms_log("info", sms_msg, db_req_q, db_res_sms_q)
        
        else:
            SMSWorker._sms_log("general", sms_msg, db_req_q, db_res_sms_q)


    @staticmethod
    def _send_sms(sms_user: SMSUser, sms_msg: SMSMsg, db_req_q: Queue, db_res_sms_q: Queue) -> None:
        ts = TwilioSender()

        # auto (special keyword) scenarios and user error
        if sms_msg.auto_status == "unsub":
            logger.info("not sending sms because unsub keyword received from phone number: {0}".format(sms_user.phone_num))

        elif sms_user.status == "unsub":
            logger.info("not sending sms because phone number: {0} has an unsub status".format(sms_user.phone_num))

        elif sms_user.user_error:
            SMSWorker._send_service_error_sms(ts, sms_user.phone_num, db_req_q, db_res_sms_q)

        elif sms_msg.auto_status == "sub":
            if sms_user.auth_status == "not auth":
                SMSWorker._send_need_auth(ts, sms_user.phone_num, db_req_q, db_res_sms_q)
            elif sms_user.status == "needs setup":
                SMSWorker._send_needs_setup_sms(ts, sms_user, db_req_q, db_res_sms_q)
            else:
                SMSWorker._send_sub_sms(ts, sms_user.phone_num, db_req_q, db_res_sms_q)

        elif sms_msg.auto_status == "info":
            if sms_user.auth_status == "not auth":
                SMSWorker._send_need_auth(ts, sms_user.phone_num, db_req_q, db_res_sms_q)
            elif sms_user.status == "needs setup":
                SMSWorker._send_needs_setup_sms(ts, sms_user, db_req_q, db_res_sms_q)
            else:
                SMSWorker._send_user_info_sms(ts, sms_user, db_req_q, db_res_sms_q)

        # new user scenarios
        elif sms_user.new_user and sms_user.auth_status == "auth":
            SMSWorker._send_auth_success(ts, sms_user.phone_num, db_req_q, db_res_sms_q)                
        
        # existing user scenarios
        else:
            if sms_user.auth_status == "not auth":
                SMSWorker._send_need_auth(ts, sms_user.phone_num, db_req_q, db_res_sms_q)
            elif sms_user.new_auth and sms_user.auth_status == "auth":
                SMSWorker._send_auth_success(ts, sms_user.phone_num, db_req_q, db_res_sms_q)
            elif sms_user.place_id_search_status == "error":
                SMSWorker._send_service_error_sms(ts, sms_user.phone_num, db_req_q, db_res_sms_q)
            elif sms_user.place_id_search_status == "no results":
                SMSWorker._send_no_results(ts, sms_user, db_req_q, db_res_sms_q)
            elif sms_user.place_id_formatted_addr:
                SMSWorker._send_addr_check(ts, sms_user, db_req_q, db_res_sms_q)
            elif sms_user.status == "needs setup":
                SMSWorker._send_needs_setup_sms(ts, sms_user, db_req_q, db_res_sms_q)
            else:
                SMSWorker._send_user_info_sms(ts, sms_user, db_req_q, db_res_sms_q)

     
    @staticmethod
    def _search_place_id(sms_msg: SMSMsg, sms_user: SMSUser) -> list[str, str]:
        pf = PlaceFinder(sms_msg.sms_body)
        logger.info("attempting to search for place id based on '{0}' for {1}".format(sms_msg.sms_body, sms_user.phone_num))
        place_finder_results = pf.search_for_place_id()
        logger.info("search results: {0}".format(place_finder_results))

        sms_user.place_id_search_status = place_finder_results.get("search_status")
        if sms_user.place_id_search_status == "ok":
            sms_user.place_id_formatted_addr = place_finder_results.get("addr")
            return [sms_user.place_id_search_status, place_finder_results.get("place_id")]

        return [sms_user.place_id_search_status, None]

    @staticmethod
    def _set_id_search_status(place_id_search_results: list, sms_user: SMSUser) -> None:
        
        if place_id_search_results[0] == "no results":
            logger.warning("no place finder results returned")
            sms_user.place_id_search_status = "no results"
        elif place_id_search_results[0] == "ok":
            sms_user.place_id_search_status = "ok"
        else:
            logger.error("problem getting place id")
            sms_user.place_id_search_status = "error"
        

    @staticmethod
    def _setup_place_id(sms_msg: SMSMsg, sms_user: SMSUser) -> None:        
        if sms_user.origin_place_id:
            if sms_user.origin_place_id_confirmed != "yes":
                if sms_msg.sms_body.replace(" ", "").lower() == "correct":
                    logger.info("user confirmed origin address")
                    sms_user.origin_place_id_confirmed = "yes"
                else:
                    logger.info("user did not confirm origin address - search again")
                    place_id_search_result = SMSWorker._search_place_id(sms_msg, sms_user)                    
                    if place_id_search_result[1]:
                        logger.info("setting origin place id to {0}".format(place_id_search_result[1]))
                        sms_user.origin_place_id = place_id_search_result[1]
                    else:
                        SMSWorker._set_id_search_status(place_id_search_result, sms_user)

            elif sms_user.dest_place_id:
                if sms_user.dest_place_id_confirmed != "yes":
                    if sms_msg.sms_body.replace(" ","").lower() == "correct":
                        logger.info("user confirmed destination address")
                        sms_user.dest_place_id_confirmed = "yes"
                    else:
                        logger.info("user did not confirm destination address - search again")
                        place_id_search_result = SMSWorker._search_place_id(sms_msg, sms_user)
                        if place_id_search_result[1]:
                            logger.info("setting destination place id to {0}".format(place_id_search_result[1]))
                            sms_user.dest_place_id = place_id_search_result[1]
                        else:
                            SMSWorker._set_id_search_status(place_id_search_result, sms_user)
            else:
                logger.info("searching for destination place id")
                place_id_search_result = SMSWorker._search_place_id(sms_msg, sms_user)
                if place_id_search_result[1]:
                    logger.info("setting destination place id to {0}".format(place_id_search_result[1]))
                    sms_user.dest_place_id = place_id_search_result[1]
                else:
                    SMSWorker._set_id_search_status(place_id_search_result, sms_user)
                                
        else:
            logger.info("searching for origin place id")
            place_id_search_result = SMSWorker._search_place_id(sms_msg, sms_user)
            if place_id_search_result[1]:
                logger.info("setting origin place id to {0}".format(place_id_search_result[1]))
                sms_user.origin_place_id = place_id_search_result[1]
            else:
                SMSWorker._set_id_search_status(place_id_search_result, sms_user)


    @staticmethod
    def _update_user_attributes(sms_user: SMSUser, sms_msg: SMSMsg) -> None:
        if sms_msg.auto_status == "unsub":
            sms_user.status = "unsub"
        elif sms_msg.auto_status == "sub" and sms_user.origin_place_id_confirmed == "yes" and sms_user.dest_place_id_confirmed == "yes":
            sms_user.status = "sub"
        elif sms_msg.auto_status == "sub" and (sms_user.origin_place_id_confirmed == "no" or sms_user.dest_place_id_confirmed == "no"):
            sms_user.status = "needs setup"
        
        if sms_msg.auto_status == "not-auto":
            if sms_user.auth_status != "auth":
                logger.info("user is not authorized - checking message for auth status")
                if SMSWorker._check_auth(sms_msg):
                    logger.info("user provided the correct pass phrase - authorizing")
                    sms_user.auth_status = "auth"
                    sms_user.new_auth = True
                else:
                    logger.info("user did not provide the correct pass phrase")
                    sms_user.auth_status = "not auth"
            elif sms_user.auth_status == "auth" and sms_user.status == "needs setup":
                logger.info("user needs setup - run place id search routine")
                SMSWorker._setup_place_id(sms_msg, sms_user)
                if sms_user.dest_place_id_confirmed == "yes" and sms_user.origin_place_id_confirmed == "yes":
                    sms_user.status = "sub"



    @staticmethod
    def sms_worker(kill_q: Queue, db_req_q: Queue, db_res_sms_q: Queue, inbound_sms_q: Queue):

        while kill_q.empty():
            try:
                inbound_sms = inbound_sms_q.get(timeout=3)
                sms_msg = SMSMsg(inbound_sms["Body"], inbound_sms["From"], inbound_sms["received_datetime"]) 

                # log invalid phone numbers to make sure watch dog can keep track of them
                if sms_msg.from_num_status == "invalid":
                    if SMSWorker._sms_log("invalid", sms_msg, db_req_q, db_res_sms_q):
                        logger.info("logged invalid sms for phone number: {0}".format(sms_msg.from_num))
                    else:
                        logger.error("failed to log invalid sms for phone number: {0}".format(sms_msg.from_num))          

                else:
                    # since the phone number is valid, let's create a user object
                    sms_user = SMSUser(sms_msg.from_num, db_req_q, db_res_sms_q)

                    if sms_user.user_error:
                        logger.error("error creating user object with phone number: {0}".format(sms_msg.from_num))
                    
                    # log the inbound sms with appropriate categorization
                    SMSWorker._log_inbound_sms(sms_msg, db_req_q, db_res_sms_q)

                    # set appropriate user attributes based on received message
                    SMSWorker._update_user_attributes(sms_user, sms_msg)
                     
                    # create or update user
                    SMSWorker._set_user(sms_user, db_req_q, db_res_sms_q)

                    # send sms (will determine if appropriate)
                    SMSWorker._send_sms(sms_user, sms_msg, db_req_q, db_res_sms_q)

            except Empty:
                logger.debug("sms inbound queue is empty")       
