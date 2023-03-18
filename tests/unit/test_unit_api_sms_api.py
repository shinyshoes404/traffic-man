from unittest import TestCase, mock
import traffic_man.api.sms_api as api_module 
import importlib
from redis.exceptions import ResponseError

@mock.patch("traffic_man.api.sms_api.TwilioSignature")
@mock.patch("traffic_man.api.sms_api.redis.Redis")
class TestSmsApi(TestCase):

    def setUp(self):
        # doing this to make sure we get a fresh instance of the flask api for each test - important for testing @before_first_request
        importlib.reload(api_module)
        self.flask_app = api_module.sms_api
        self.flask_app.testing = True
        self.client = self.flask_app.test_client()


    ### ------------------ inbound_sms() ----------------------------------
    def test_unit_before_first_request_confirm_cons_grp_create(self, mock_redis, mock_twsig):
        self.client.get("/inbound")
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)
   
    def test_unit_before_first_request_confirm_except_raise_random_except(self, mock_redis, mock_twsig):
        mock_redis.return_value.xgroup_create.side_effect = Exception("bad exception")
        test_resp = self.client.post("/inbound")
        self.assertEqual(test_resp.status_code, 500)
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)

    def test_unit_before_first_request_confirm_except_raise_wrong_response_error(self, mock_redis, mock_twsig):
        mock_redis.return_value.xgroup_create.side_effect = ResponseError("bad exception")
        test_resp = self.client.post("/inbound")
        self.assertEqual(test_resp.status_code, 500)    
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)

    def test_unit_inbound_sms_twilio_sig_not_match(self, mock_redis, mock_twsig):
        mock_redis.return_value.xgroup_create.side_effect = ResponseError("BUSYGROUP Consumer Group name already exists")
        mock_twsig.return_value.compare_signatures.return_value = False
        test_resp = self.client.post("/inbound")
        self.assertEqual(test_resp.status_code, 403)
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)

    def test_unit_inbound_sms_twilio_sig_match_xadd_except(self, mock_redis, mock_twsig):
        mock_redis.return_value.xgroup_create.side_effect = ResponseError("BUSYGROUP Consumer Group name already exists")
        mock_twsig.return_value.compare_signatures.return_value = True
        mock_redis.return_value.xadd.side_effect = Exception("couldn't add msg")
        test_resp = self.client.post("/inbound",headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"MessageSid":"messagesid", "From":"+15555555555", "To":"+12222222222"})
        self.assertEqual(test_resp.status_code, 500)
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)
        self.assertEqual(mock_redis.return_value.xadd.call_count, 1)

    def test_unit_inbound_sms_twilio_sig_match_everything_works(self, mock_redis, mock_twsig):
        mock_redis.return_value.xgroup_create.side_effect = ResponseError("BUSYGROUP Consumer Group name already exists")
        mock_twsig.return_value.compare_signatures.return_value = True
        test_resp = self.client.post("/inbound",headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"MessageSid":"messagesid", "From":"+15555555555", "To":"+12222222222"})
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(mock_redis.return_value.xgroup_create.call_count, 1)
        self.assertEqual(mock_redis.return_value.xadd.call_count, 1)