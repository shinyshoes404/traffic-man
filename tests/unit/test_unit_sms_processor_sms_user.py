from unittest import TestCase, mock
from traffic_man.sms_processor.sms_user import SMSUser

class TestSMSMsg(TestCase):
    ### ---------------- SMSUser.__init__() ----------------
    def test_unit_smsuser_user_error(self):
        with mock.patch('traffic_man.sms_processor.sms_user.SMSDataMgr.get_user_by_phone_num', return_value=False) as mock_get_user:
            mock_db_req_q = mock.Mock()
            mock_db_res_sms_q = mock.Mock()

            test_sms_user = SMSUser("+12222222222", mock_db_req_q, mock_db_res_sms_q)
            self.assertIs(test_sms_user.user_error, True)

    def test_unit_smsuser_no_user_exists(self):
        with mock.patch('traffic_man.sms_processor.sms_user.SMSDataMgr.get_user_by_phone_num', return_value=None) as mock_get_user:
            mock_db_req_q = mock.Mock()
            mock_db_res_sms_q = mock.Mock()

            test_sms_user = SMSUser("+12222222222", mock_db_req_q, mock_db_res_sms_q)
            self.assertIs(test_sms_user.user_error, False)
            self.assertIs(test_sms_user.new_user, True)
            self.assertIs(test_sms_user.origin_place_id, None)
            self.assertIs(test_sms_user.dest_place_id, None)
            self.assertEqual(test_sms_user.status, "needs setup")
            self.assertEqual(test_sms_user.auth_status, "not auth")

    def test_unit_smsuser_user_exists(self):
        fake_user_results = {
            "phone_num": "+13333333333",
            "origin_place_id": None,
            "dest_place_id": None,
            "status": "subscribe",
            "auth_status": "not auth"
        }
        with mock.patch('traffic_man.sms_processor.sms_user.SMSDataMgr.get_user_by_phone_num', return_value=fake_user_results) as mock_get_user:
            mock_db_req_q = mock.Mock()
            mock_db_res_sms_q = mock.Mock()

            test_sms_user = SMSUser("phone num as str", mock_db_req_q, mock_db_res_sms_q)
            self.assertIs(test_sms_user.user_error, False)
            self.assertIs(test_sms_user.new_user, False)
            self.assertEqual(test_sms_user.origin_place_id, fake_user_results["origin_place_id"])
            self.assertEqual(test_sms_user.dest_place_id, fake_user_results["dest_place_id"])
            self.assertEqual(test_sms_user.status, fake_user_results["status"])
            self.assertEqual(test_sms_user.auth_status, fake_user_results["auth_status"])