from unittest import TestCase, mock
from queue import Empty

from traffic_man.traffic_engine.traffic_data_manager import TrafficDataMgr

@mock.patch("traffic_man.traffic_engine.traffic_data_manager.uuid.uuid4")
class TestTrafficDataMgrDBOps(TestCase):

    ### --------------------- TrafficDataMgr.get_next_run() ----------------------
    def test_get_next_run_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        check_val_1, check_val_2 = TrafficDataMgr.get_next_run(mock_db_req_q, mock_db_res_traf_eng_q)
        self.assertIs(check_val_1, False)
        self.assertIs(check_val_2, False)
    
    def test_get_next_run_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": (30, False)}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        check_val_1, check_val_2 = TrafficDataMgr.get_next_run(mock_db_req_q, mock_db_res_traf_eng_q)
        self.assertIs(check_val_1, False)
        self.assertIs(check_val_2, False)

    def test_get_next_run_return_result(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": (30, True)}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        check_val_1, check_val_2 = TrafficDataMgr.get_next_run(mock_db_req_q, mock_db_res_traf_eng_q)
        self.assertEqual(check_val_1, 30)
        self.assertIs(check_val_2, True)

    ### --------------------- TrafficDataMgr.get_orig_dest_pairs() ----------------------
    def test_get_orig_dest_pairs_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        self.assertIs(TrafficDataMgr.get_orig_dest_pairs(mock_db_req_q, mock_db_res_traf_eng_q), False)

    def test_get_orig_dest_pairs_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": [["orig1", "dest1"], ["orig2", "dest2"]]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        self.assertIs(TrafficDataMgr.get_orig_dest_pairs(mock_db_req_q, mock_db_res_traf_eng_q), False)

    def test_get_orig_dest_pairs_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": [["orig1", "dest1"], ["orig2", "dest2"]]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        self.assertEqual(TrafficDataMgr.get_orig_dest_pairs(mock_db_req_q, mock_db_res_traf_eng_q), [["orig1", "dest1"], ["orig2", "dest2"]])

    ### --------------------- TrafficDataMgr.get_traffic_cond_data() ----------------------
    def test_get_traffic_cond_data_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        self.assertIs(TrafficDataMgr.get_traffic_cond_data(mock_db_req_q, mock_db_res_traf_eng_q), False)

    def test_get_traffic_cond_data_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        self.assertIs(TrafficDataMgr.get_traffic_cond_data(mock_db_req_q, mock_db_res_traf_eng_q), False)

    def test_get_traffic_cond_data_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        self.assertEqual(TrafficDataMgr.get_traffic_cond_data(mock_db_req_q, mock_db_res_traf_eng_q), ["random", "results"])


    ### --------------------- TrafficDataMgr.store_traffic_data() ----------------------
    def test_store_traffic_data_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        traffic_data = {"fake": "data"}

        self.assertIs(TrafficDataMgr.store_traffic_data(mock_db_req_q, mock_db_res_traf_eng_q, traffic_data), False)

    def test_store_traffic_data_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        traffic_data = {"fake": "data"}

        self.assertIs(TrafficDataMgr.store_traffic_data(mock_db_req_q, mock_db_res_traf_eng_q, traffic_data), False)

    def test_store_traffic_data_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"
        traffic_data = {"fake": "data"}

        self.assertEqual(TrafficDataMgr.store_traffic_data(mock_db_req_q, mock_db_res_traf_eng_q, traffic_data), ["random", "results"])


    ### --------------------- TrafficDataMgr.store_new_bad_traffic() ----------------------
    def test_store_new_bad_traffic_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertIs(TrafficDataMgr.store_new_bad_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), False)

    def test_store_new_bad_traffic_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertIs(TrafficDataMgr.store_new_bad_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), False)

    def test_store_new_bad_traffic_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"
        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertEqual(TrafficDataMgr.store_new_bad_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), ["random", "results"])

     ### --------------------- TrafficDataMgr.store_resolved_traffic() ----------------------
    def test_store_resolved_traffic_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertIs(TrafficDataMgr.store_resolved_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), False)

    def test_store_resolved_traffic_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertIs(TrafficDataMgr.store_resolved_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), False)

    def test_store_resolved_traffic_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"
        fake_orig_id = "orig1"
        fake_dest_id = "dest1"

        self.assertEqual(TrafficDataMgr.store_resolved_traffic(mock_db_req_q, mock_db_res_traf_eng_q, fake_orig_id, fake_dest_id), ["random", "results"]) 


     ### --------------------- TrafficDataMgr.get_phone_nums() ----------------------
    def test_get_phone_nums_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"
        sms_type = "fake-sms-type"

        self.assertIs(TrafficDataMgr.get_phone_nums(mock_db_req_q, mock_db_res_traf_eng_q, sms_type ,fake_orig_id, fake_dest_id), False)

    def test_get_phone_nums_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        fake_orig_id = "orig1"
        fake_dest_id = "dest1"
        sms_type = "fake-sms-type"

        self.assertIs(TrafficDataMgr.get_phone_nums(mock_db_req_q, mock_db_res_traf_eng_q, sms_type, fake_orig_id, fake_dest_id), False)

    def test_get_phone_nums_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"
        fake_orig_id = "orig1"
        fake_dest_id = "dest1"
        sms_type = "fake-sms-type"

        self.assertEqual(TrafficDataMgr.get_phone_nums(mock_db_req_q, mock_db_res_traf_eng_q, sms_type, fake_orig_id, fake_dest_id), ["random", "results"]) 


     ### --------------------- TrafficDataMgr.store_sms_data() ----------------------
    def test_store_sms_data_timeout(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        mock_db_res_traf_eng_q.get.side_effect = Empty

        fake_sms_data = ["fake", "data"]

        self.assertIs(TrafficDataMgr.store_sms_data(mock_db_req_q, mock_db_res_traf_eng_q, fake_sms_data), False)

    def test_store_sms_data_wrong_msgid(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "wrongid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"

        fake_sms_data = ["fake", "data"]

        self.assertIs(TrafficDataMgr.store_sms_data(mock_db_req_q, mock_db_res_traf_eng_q, fake_sms_data), False)

    def test_store_sms_data_return_results(self, mock_uuid4):
        mock_db_req_q = mock.Mock()
        mock_db_res_traf_eng_q = mock.Mock()
        fake_return_data = {"msg-id": "randomuuid", "msg_src": "traffic_engine", "results": ["random", "results"]}
        mock_db_res_traf_eng_q.get.return_value = fake_return_data

        mock_uuid4.return_value = "randomuuid"
        fake_sms_data = ["fake", "data"]

        self.assertEqual(TrafficDataMgr.store_sms_data(mock_db_req_q, mock_db_res_traf_eng_q, fake_sms_data), ["random", "results"]) 


class TestTrafficDataMgrProcData(TestCase):

    ### --------------------- TrafficDataMgr.proc_bad_traffic_data() ----------------------
    def test_proc_bad_traffic_data_no_data_provided(self):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()
        
        self.assertIs(TrafficDataMgr.proc_bad_traffic_data(mock_db_req_q, mock_db_res_traff_eng_q, None), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_manager.TrafficDataMgr.get_phone_nums")
    @mock.patch("traffic_man.traffic_engine.traffic_data_manager.TrafficDataMgr.store_new_bad_traffic")
    def test_proc_bad_traffic_data_all_combos_return_value(self, mock_store_bad_traff, mock_get_phone_nums):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        fake_bad_traffic_data = [
            {"orig_place_id": "orig1", "dest_place_id": "dest1"},
            {"orig_place_id": "orig2", "dest_place_id": "dest2"},
            {"orig_place_id": "orig3", "dest_place_id": "dest3"}
        ]

        mock_store_bad_traff.side_effect = [False, True, True ]
        mock_get_phone_nums.side_effect = [False, [("+12222222222",), ("+13333333333",)]]

        check_val = TrafficDataMgr.proc_bad_traffic_data(mock_db_req_q, mock_db_res_traff_eng_q, fake_bad_traffic_data)

        self.assertEqual(mock_get_phone_nums.call_count, 2)
        self.assertEqual(check_val, [("+12222222222",), ("+13333333333",)])


    ### --------------------- TrafficDataMgr.proc_resolved_traffic_data() ----------------------
    def test_proc_resolved_traffic_data_no_data_provided(self):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()
        
        self.assertIs(TrafficDataMgr.proc_resolved_traffic_data(mock_db_req_q, mock_db_res_traff_eng_q, None), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_manager.TrafficDataMgr.get_phone_nums")
    @mock.patch("traffic_man.traffic_engine.traffic_data_manager.TrafficDataMgr.store_resolved_traffic")
    def test_proc_resolved_traffic_data_all_combos_return_value(self, mock_store_resolved_traff, mock_get_phone_nums):
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        fake_resolved_traffic_data = [
            {"orig_place_id": "orig1", "dest_place_id": "dest1"},
            {"orig_place_id": "orig2", "dest_place_id": "dest2"},
            {"orig_place_id": "orig3", "dest_place_id": "dest3"}
        ]

        mock_store_resolved_traff.side_effect = [False, True, True ]
        mock_get_phone_nums.side_effect = [False, [("+12222222222",), ("+13333333333",)]]

        check_val = TrafficDataMgr.proc_resolved_traffic_data(mock_db_req_q, mock_db_res_traff_eng_q, fake_resolved_traffic_data)

        self.assertEqual(mock_get_phone_nums.call_count, 2)
        self.assertEqual(check_val, [("+12222222222",), ("+13333333333",)])
  