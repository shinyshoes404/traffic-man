from traffic_man.config import Config
from traffic_man.sms_processor.sms_messages import SMSMsg
from flask import Flask, request, make_response
from flask_cors import CORS
import redis, datetime

from traffic_man.twilio.twilio import TwilioSignature

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

sms_api = Flask(__name__)

CORS(sms_api)
# gloabl var to keep track of redis consumer group issues
redis_cons_grp_status = "no error"

@sms_api.before_first_request
def _redis_create_consumer_grp():   
    global redis_cons_grp_status
    redis_conn = redis.Redis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db, password=Config.redis_pw, decode_responses=True)
    try:
        redis_conn.xgroup_create(name=Config.redis_sms_stream_key, groupname=Config.redis_sms_consum_grp, mkstream=True, id="$")
        logger.info("created consumer group: {0}".format(Config.redis_sms_consum_grp))
    except redis.exceptions.ResponseError as e:
        if str(e) == "BUSYGROUP Consumer Group name already exists":
            logger.info("consumer group {0} already exists - moving on".format(Config.redis_sms_consum_grp))
        else:
            logger.error("problem creating consumer group in redis")
            logger.error(e)
            redis_cons_grp_status = "error"
    except Exception as e:
        logger.error("problem creating consumer group in redis")
        logger.error(e)
        redis_cons_grp_status = "error"


def _sms_msg_producer(msg: dict) -> bool:
    redis_conn = redis.Redis(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db, password=Config.redis_pw, decode_responses=True)
    msg["received_datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        redis_conn.xadd(Config.redis_sms_stream_key, msg, "*")
    except Exception as e:
        logger.error("problem publishing message to redis stream msg: {0}".format(msg))
        logger.error(e)
        return False
    
    return True


@sms_api.route("/inbound", methods=["POST"])
def inbound_sms():
    global redis_cons_grp_status
    if redis_cons_grp_status == "error":
        resp = make_response("internal server error", 500)
        return(resp)

    req_headers = request.headers
    twilio_sig = TwilioSignature(request, req_headers)
    logger.info("twilio signature: {0}".format(twilio_sig._create_signature()))
    if not twilio_sig.compare_signatures():
        resp = make_response("not authorized", 403)
        return resp
    
    req_data = request.form.to_dict()

    if not _sms_msg_producer(req_data):
        resp = make_response("internal server error", 500)
        return resp

    resp = make_response("<Response></Response>", 200)
    resp.headers["Content-Type"] = "text/html"
    return resp




