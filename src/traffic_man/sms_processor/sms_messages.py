from traffic_man.config import Config

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSMsg:
    auto_reply_words = {
        "unsubscribe": ["stop", "stopall", "unsubscribe", "cancel", "quit", "end"],
        "subscribe": ["start", "yes", "unstop"],
        "info": ["help", "info"]
    }

    def __init__(self, sms_body: str, from_num: str, msg_rec_datetime: str):
        self.sms_body = sms_body
        self.from_num = from_num
        self.msg_rec_datetime = msg_rec_datetime
        self._set_auto_status()
        self._check_from_num_format()
        self._check_msg_length()
    
    def _set_auto_status(self) -> None:

        if self.sms_body.replace(" ", "").lower() in self.auto_reply_words["unsubscribe"]:
            self.auto_status = "unsub"
        elif self.sms_body.replace(" ", "").lower() in self.auto_reply_words["subscribe"]:
            self.auto_status = "sub"
        elif self.sms_body.replace(" ", "").lower() in self.auto_reply_words["info"]:
            self.auto_status = "info"
        else:
            self.auto_status = "not-auto"

        return None
    
    def _check_from_num_format(self) -> None:
        if len(self.from_num) != 12 or self.from_num[:2] != "+1":
            self.from_num_status = "invalid"
            if len(self.from_num) >= 12:
                self.from_num = self.from_num[:12]
        
        else:
            self.from_num_status = "valid"
        
        return None
    
    def _check_msg_length(self) -> None:
        if len(self.sms_body) > 160:
            self.msg_trunc_status = "truncated"
            self.sms_body = self.sms_body[:160]
        else:
            self.msg_trunc_status = "unaltered"
        
        return None
    

        
        
    

