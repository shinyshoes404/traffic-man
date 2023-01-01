from unittest import TestCase, mock

from traffic_man.traffic_engine.traffic_messaging import TrafficMessenger


@mock.patch("traffic_man.traffic_engine.traffic_messaging.TwilioSender")
class TestTrafficMessenger(TestCase):

    ### --------------------- TrafficMessenger.send_bad_traffic_sms() ----------------------
    def test_send_bad_traffic_sms_no_send_results(self, mock_twilio_sender):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_twilio_sender.return_value.send_bad_traffic_sms.return_value = []

        phone_num_list = []
        self.assertIs(TrafficMessenger.send_bad_traffic_sms(mock_db_req_q, mock_db_res_traff_eng_q, phone_num_list), None)

    def test_send_bad_traffic_sms_results_returned(self, mock_twilio_sender):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_twilio_sender.return_value.send_bad_traffic_sms.return_value = ["some send result"]

        phone_num_list = ["+12222222222"]

        with mock.patch("traffic_man.traffic_engine.traffic_messaging.TrafficDataMgr.store_sms_data", return_value=True) as mock_store_sms:
            self.assertEqual(TrafficMessenger.send_bad_traffic_sms(mock_db_req_q, mock_db_res_traff_eng_q, phone_num_list), True)

    ### --------------------- TrafficMessenger.send_resolved_traffic_sms() ----------------------
    def test_send_resolved_traffic_sms_no_send_results(self, mock_twilio_sender):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_twilio_sender.return_value.send_resolved_traffic_sms.return_value = []

        phone_num_list = []
        self.assertIs(TrafficMessenger.send_resolved_traffic_sms(mock_db_req_q, mock_db_res_traff_eng_q, phone_num_list), None)

    def test_send_resolved_traffic_sms_results_returned(self, mock_twilio_sender):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_twilio_sender.return_value.send_resolved_traffic_sms.return_value = ["some send result"]

        phone_num_list = ["+12222222222"]

        with mock.patch("traffic_man.traffic_engine.traffic_messaging.TrafficDataMgr.store_sms_data", return_value=True) as mock_store_sms:
            self.assertEqual(TrafficMessenger.send_resolved_traffic_sms(mock_db_req_q, mock_db_res_traff_eng_q, phone_num_list), True)
