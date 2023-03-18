from unittest import TestCase, mock
from traffic_man.sms_processor.sms_messages import SMSMsg

class TestSMSMsg(TestCase):
    ### ---------------- SMSMsg.__init__() ----------------
    def test_smsmsg_auto_status_unsub(self):
        sms_msg = SMSMsg(" stoP ", "+12222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.auto_status, "unsub")

    def test_smsmsg_auto_status_sub(self):
        sms_msg = SMSMsg(" sTarT ", "+12222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.auto_status, "sub")

    def test_smsmsg_auto_status_info(self):
        sms_msg = SMSMsg(" HElP ", "+12222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.auto_status, "info")
    
    def test_smsmsg_not_auto_status(self):
        sms_msg = SMSMsg("some message", "+12222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.auto_status, "not-auto")
        self.assertEqual(sms_msg.msg_trunc_status, "unaltered")
        self.assertEqual(sms_msg.from_num_status, "valid")

    def test_smsmsg_invalid_phone_number(self):
        sms_msg = SMSMsg("some message", "+432222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.from_num_status, "invalid")

    def test_smsmsg_truc_msg(self):
        message = "hello there this is a really really long sms message which will get truncated by Traffic Man, because it is longer than 160 characters which is standard for SMS messaging."
        sms_msg = SMSMsg(message, "+12222222222", "2022-01-02 10:13:05")
        self.assertEqual(sms_msg.msg_trunc_status, "truncated")
        self.assertEqual(sms_msg.sms_body, message[:160])
