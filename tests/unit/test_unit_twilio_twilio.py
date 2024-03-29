from unittest import TestCase, mock
import os, requests
from traffic_man.twilio.twilio import TwilioSender, TwilioSignature

class TestTwilioSender(TestCase):
    ### ---------------- TwilioSender.__init__() ----------------    
    # just verifying that the base64 encoding is working properly for basic auth
    def test_unit_TwilioSender_init(self):
        with mock.patch.dict(os.environ, {"TWILIO_ACCOUNT_SID":"fake-twilio-sid", "TWILIO_AUTH_TOKEN":"fake-twilio-token", "FROM_NUM":"+15555555555"}, clear=True ) as mock_env:
            twilio_sender = TwilioSender()
            test_headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            print("from num ----- {0}".format(twilio_sender.from_phone))
            self.assertEqual(twilio_sender.headers, test_headers)

    ### ---------------- TwilioSender.send_bad_traffic_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_bad_traffic_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_bad_traffic_sms(["+15555555555", "+14444444444"])
            self.assertEqual(len(check_val), 2)
            self.assertEqual(mock_send_retry.call_count,2)
            self.assertEqual(check_val[0]["status"], "sent")

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_bad_traffic_sms_one_error(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", side_effect=[None, True]) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_bad_traffic_sms(["+15555555555", "+13333333333"])
            self.assertEqual(len(check_val), 2)
            self.assertEqual(mock_send_retry.call_count,2)
            self.assertEqual(check_val[0]["status"], "failed")

    ### ---------------- TwilioSender.send_resolved_traffic_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_resolved_traffic_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_resolved_traffic_sms(["+15555555555", "+14444444444"])
            self.assertEqual(len(check_val), 2)
            self.assertEqual(mock_send_retry.call_count,2)
            self.assertEqual(check_val[0]["status"], "sent")

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_resolved_traffic_sms_one_error(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", side_effect=[None, True]) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_resolved_traffic_sms(["+15555555555", "+13333333333"])
            self.assertEqual(len(check_val), 2)
            self.assertEqual(mock_send_retry.call_count,2)
            self.assertEqual(check_val[0]["status"], "failed")


    ### ---------------- TwilioSender.send_sub_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sub_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_sub_sms("+12222222222")
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sub_sms_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_sub_sms("+12222222222")
            self.assertIs(check_val_sent, False)


    ### ---------------- TwilioSender.send_need_auth_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_need_auth_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_need_auth_sms("+12222222222")
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_need_auth_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_need_auth_sms("+12222222222")
            self.assertIs(check_val_sent, False)


    ### ---------------- TwilioSender.send_auth_failed_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_auth_failed_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_auth_failed_sms("+12222222222")
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_auth_failed_sms_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_auth_failed_sms("+12222222222")
            self.assertIs(check_val_sent, False)


    ### ---------------- TwilioSender.send_auth_success_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_auth_success_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_auth_success_sms("+12222222222")
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_auth_success_sms_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_auth_success_sms("+12222222222")
            self.assertIs(check_val_sent, False)


    ### ---------------- TwilioSender.send_service_error_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_service_error_sms_no_errors(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_service_error_sms("+12222222222")
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_service_error_sms_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_service_error_sms("+12222222222")
            self.assertIs(check_val_sent, False)      


    ### ---------------- TwilioSender.send_needs_setup_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_needs_setup_sms_no_errors_origin(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            mock_user = mock.Mock()
            mock_user.phone_num = "+12222222222"
            mock_user.origin_place_id_confirmed = "no"
            mock_user.dest_place_id_confirmed = "no"

            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_needs_setup_sms(mock_user)
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_needs_setup_sms_no_errors_destination(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            mock_user = mock.Mock()
            mock_user.phone_num = "+12222222222"
            mock_user.origin_place_id_confirmed = "yes"
            mock_user.dest_place_id_confirmed = "no"

            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_needs_setup_sms(mock_user)
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_needs_setup_sms_failed(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            mock_user = mock.Mock()
            mock_user.phone_num = "+12222222222"
            mock_user.origin_place_id_confirmed = "no"
            mock_user.dest_place_id_confirmed = "no"

            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_needs_setup_sms(mock_user)
            self.assertIs(check_val_sent, False)  

    ### ---------------- TwilioSender.send_no_results_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_no_results_sms_no_errors(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_no_results_sms(mock_user)
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_no_results_sms_failed(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_no_results_sms(mock_user)
            self.assertIs(check_val_sent, False)  

    ### ---------------- TwilioSender.send_user_info_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_user_info_sms_no_errors(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"
        mock_user.origin_place_id = "orig1"
        mock_user.dest_place_id = "dest1"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_user_info_sms(mock_user)
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_user_info_sms_failed(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"
        mock_user.origin_place_id = "orig1"
        mock_user.dest_place_id = "dest1"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_user_info_sms(mock_user)
            self.assertIs(check_val_sent, False)  

    ### ---------------- TwilioSender.send_addr_check() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_addr_check_no_errors(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=True) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_addr_check(mock_user)
            self.assertIs(check_val_sent, True)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_addr_check_failed(self, mock_init):
        mock_user = mock.Mock()
        mock_user.phone_nun = "+12222222222"

        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms_with_retry", return_value=False) as mock_send_retry:
            twilio_sender = TwilioSender()
            check_val_sent, check_val_body = twilio_sender.send_addr_check(mock_user)
            self.assertIs(check_val_sent, False)  

    ### ---------------- TwilioSender.send_sms() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_timeout_except(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout
            twilio_sender = TwilioSender()
            # setting properties, because we mocked __init__
            twilio_sender.url = "https://fakeurl"
            twilio_sender.headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            twilio_sender.from_phone = "+15555555555"
            check_val = twilio_sender.send_sms("fake body", "+13333333333")
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_ssl_except(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.SSLError
            twilio_sender = TwilioSender()
            # setting properties, because we mocked __init__
            twilio_sender.url = "https://fakeurl"
            twilio_sender.headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            twilio_sender.from_phone = "+15555555555"
            check_val = twilio_sender.send_sms("fake body", "+13333333333")
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_unexpected_except(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.requests.post") as mock_post:
            mock_post.side_effect = Exception("unexpected exception")
            twilio_sender = TwilioSender()
            # setting properties, because we mocked __init__
            twilio_sender.url = "https://fakeurl"
            twilio_sender.headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            twilio_sender.from_phone = "+15555555555"
            check_val = twilio_sender.send_sms("fake body", "+13333333333")
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_bad_request(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.requests.post") as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.content = b'bad request error'
            twilio_sender = TwilioSender()
            # setting properties, because we mocked __init__
            twilio_sender.url = "https://fakeurl"
            twilio_sender.headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            twilio_sender.from_phone = "+15555555555"
            check_val = twilio_sender.send_sms("fake body", "+13333333333")
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_success(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.requests.post") as mock_post:
            mock_post.return_value.status_code = 201
            twilio_sender = TwilioSender()
            # setting properties, because we mocked __init__
            twilio_sender.url = "https://fakeurl"
            twilio_sender.headers = {"Authorization": "Basic ZmFrZS10d2lsaW8tc2lkOmZha2UtdHdpbGlvLXRva2Vu", "Content-Type": "application/x-www-form-urlencoded"}
            twilio_sender.from_phone = "+15555555555"
            check_val = twilio_sender.send_sms("fake body", "+13333333333")
            self.assertIs(check_val, True)
    
    ### ---------------- TwilioSender.send_sms_with_retry() ----------------
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_with_retry_send_first_try(self, mock_init):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms", return_value=True) as mock_send_sms:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_sms_with_retry(2, "fake body", "+13333333333")
            self.assertIs(check_val, True)

    @mock.patch("traffic_man.twilio.twilio.sleep", return_value=None)
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_with_retry_send_second_try(self, mock_init, mock_sleep):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms", side_effect=[None, True]) as mock_send_sms:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_sms_with_retry(2, "fake body", "+13333333333")
            self.assertIs(check_val, True)
            self.assertEqual(mock_send_sms.call_count, 2)

    @mock.patch("traffic_man.twilio.twilio.sleep", return_value=None)
    @mock.patch("traffic_man.twilio.twilio.TwilioSender.__init__", return_value=None) # mocking __init__ to avoid env var management, etc
    def test_unit_send_sms_with_retry_exceed_retries(self, mock_init, mock_sleep):
        with mock.patch("traffic_man.twilio.twilio.TwilioSender.send_sms", side_effect=[None, None]) as mock_send_sms:
            twilio_sender = TwilioSender()
            check_val = twilio_sender.send_sms_with_retry(2, "fake body", "+13333333333")
            self.assertIs(check_val, None)
            self.assertEqual(mock_send_sms.call_count, 2)



class TestTwilioSignature(TestCase):
    ### ---------------- TwilioSignatue.compare_signatures() ----------------
    def test_unit_twilio_header_missing(self):
        mock_req_body = mock.Mock()
        test_headers = {"X-Wrong-Header": "some-data"}
        test_obj = TwilioSignature(mock_req_body, test_headers)
        self.assertIs(test_obj.compare_signatures(), False)

    @mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "ABC123", "TWILIO_WEBHOOK_URL": "https://example.com"})
    def test_unit_signature_doesnt_match(self):
        mock_req_body = mock.Mock()
        mock_req_body.form.to_dict = mock.PropertyMock(return_value={"key1": "val1", "key2": "val2"})

        test_headers = {"X-Twilio-Signature": "wrong-signature"}

        test_obj = TwilioSignature(mock_req_body, test_headers)
        self.assertIs(test_obj.compare_signatures(), False)

    @mock.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "ABC123", "TWILIO_WEBHOOK_URL": "https://example.com"})
    def test_unit_signature_matches(self):
        mock_req_body = mock.Mock()
        mock_req_body.form.to_dict = mock.PropertyMock(return_value={"key1": "val1", "key2": "val2"})
        test_headers = {"X-Twilio-Signature": "xUiKdFeXAF4O8V0PomCvfQCPkxg="}

        test_obj = TwilioSignature(mock_req_body, test_headers)
        self.assertIs(test_obj.compare_signatures(), True)