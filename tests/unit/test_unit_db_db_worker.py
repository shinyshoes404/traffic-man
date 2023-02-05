from unittest import TestCase, mock
from queue import Empty
from traffic_man.db.db_worker import db_worker

mock_class = mock.Mock()
mock_class.mock_method.return_value = mock.PropertyMock(new_callable=mock.Mock())
fake_mapping = {
    "FAKECOMMAND": {"class": mock_class, "method": mock_class.mock_method}
}

mock_db_ops_map_obj = mock.Mock()
mock_db_ops_map_obj.get.return_value = mock.PropertyMock(new_callable=mock.Mock())

@mock.patch("traffic_man.db.db_worker.db.create_engine", return_value=mock.Mock())
@mock.patch("traffic_man.db.db_worker.metadata_obj.create_all")
@mock.patch("traffic_man.db.db_worker.DataSetup")
@mock.patch("traffic_man.db.db_worker.db_ops_mapping", return_value=fake_mapping)
class TestDBWorker(TestCase):

    mock_kill_q = mock.Mock()
    mock_db_req_q = mock.Mock()    
    mock_db_res_traffic_eng_q = mock.Mock()
    mock_db_res_sms_q = mock.Mock()

    def setUp(self):
        # clear out mock counts and values between tests
        self.mock_db_req_q.reset_mock()
        self.mock_db_req_q.get.side_effect = None
        self.mock_db_res_traffic_eng_q.reset_mock()
        self.mock_kill_q.reset_mock()
        self.mock_db_req_q.empty.side_effect = None
        self.mock_db_res_sms_q.reset_mock()
        self.mock_db_res_sms_q.get.side_effect = None

    def test_db_worker_fail_update_check_times(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        mock_datasetup.return_value.update_check_times.return_value = None
        check_val = db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertIs(check_val, None)

    def test_db_worker_fail_update_holidays(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        mock_datasetup.return_value.update_holidays.return_value = None
        check_val = db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertIs(check_val, None)

    def test_db_worker_fail_update_check_days(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        mock_datasetup.return_value.update_check_days.return_value = None
        check_val = db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertIs(check_val, None)
    
    def test_db_worker_one_cycle_empty_q(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        self.mock_kill_q.empty.side_effect = [True, False] #cycle once, then exit loop
        self.mock_db_req_q.get.side_effect = Empty
        db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertEqual(self.mock_db_res_traffic_eng_q.put.call_count, 0)

    def test_db_worker_one_cycle_traffic_eng_src_msgid_msgsrc_present(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        self.mock_kill_q.empty.side_effect = [True, False] #cycle once, then exit loop
        fake_msg = {"msg-id": "fakeid", "msg-src": "traffic_engine", "command": "FAKECOMMAND", "class-args": [], "method-args": []}
        self.mock_db_req_q.get.return_value = fake_msg
        db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertEqual(self.mock_db_res_traffic_eng_q.put.call_count, 1)

    def test_db_worker_one_cycle_msgid_msgsrc_not_present(self, mock_map, mock_datasetup, mock_create_all, mock_create_eng):
        self.mock_kill_q.empty.side_effect = [True, False] #cycle once, then exit loop
        fake_msg = {"command": "FAKECOMMAND", "class-args": [], "method-args": []}
        self.mock_db_req_q.get.return_value = fake_msg
        db_worker(self.mock_kill_q, self.mock_db_req_q, self.mock_db_res_traffic_eng_q, self.mock_db_res_sms_q)
        self.assertEqual(self.mock_db_res_traffic_eng_q.put.call_count, 0)

