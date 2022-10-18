import os, base64, requests, logging
from traffic_man.config import Config
from time import sleep

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class TwilioSender:
    def __init__(self):
        self.url = "https://api.twilio.com/2010-04-01/Accounts/" + os.environ.get("TWILIO_ACCOUNT_SID") + "/Messages.json"
        
        basic_auth = os.environ.get("TWILIO_ACCOUNT_SID") + ":" + os.environ.get("TWILIO_AUTH_TOKEN")
        basic_auth_bytes = basic_auth.encode("utf-8")
        base64_bytes = base64.b64encode(basic_auth_bytes)
        base64_auth = base64_bytes.decode("ascii")

        self.headers = {"Authorization": "Basic " + base64_auth, "Content-Type": "application/x-www-form-urlencoded"}
        self.from_phone = os.environ.get("FROM_NUM")

    
    def send_bad_traffic_sms(self, phone_nums: list):
        logger.info("attempting to send bad traffic sms")
        body = "Traffic is looking pretty bad."
        err_count = 0
        for num in phone_nums:
           
            if not self.send_sms_with_retry(2, body, num):
                logger.error("failed to send bad traffic sms to {0}".format(num))
                err_count = err_count + 1

        return err_count
    
    def send_resolved_traffic_sms(self, phone_nums: list) -> int:
        logger.info("attempting to send traffic resolved sms")
        body = "It looks like traffic has cleared up."
        err_count = 0
        for num in phone_nums:
           
            if not self.send_sms_with_retry(2, body, num):
                logger.error("failed to send traffic resolved sms to {0}".format(num))
                err_count = err_count + 1

        return err_count


    def send_sms(self, body: str, phone_num: str) -> bool:
        logger.info("attempting to send sms")
        
        req_body = {
            "Body": body,
            "To": phone_num,
            "From": self.from_phone
        }

        try:
            resp = requests.post(url=self.url, headers=self.headers, data=req_body)
        except requests.exceptions.Timeout:
            logger.warning("twilio request timed out")
            return None
        except requests.exceptions.SSLError:
            logger.warning("twilio request experienced an SSL error")
            return None
        except Exception as e:
            logger.error("twilio request encountered an unexcpected error")
            logger.error(e)
            return None

        if resp.status_code != 201:
            logger.error("twilio request to send sms failed status code: {0} content: {1}".format(resp.status_code, resp.content))
            return None

        logger.info("sms message successfully sent to {0}".format(phone_num))
        return True

    def send_sms_with_retry(self, attempts: int, body: str, phone_num: str) -> bool:
        # attempts = total attempts, not just retries
        for i in range(0, attempts):
            sms_result = self.send_sms(body, phone_num)
            if sms_result:
                return sms_result
            if i < max(range(0, attempts)):
                logger.warning("wait before we retrys")
                sleep(10 * (i + 1))
                logger.warning("retrying twilio api call")
        logger.error("sms send exceeded the max number of attempts - max atempts: {0}".format(attempts))
        return None