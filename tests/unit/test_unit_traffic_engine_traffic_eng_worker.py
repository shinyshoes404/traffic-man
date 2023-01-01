from unittest import TestCase, mock
from datetime import datetime, timedelta

from traffic_man.traffic_engine.traffic_eng_worker import TrafficEngine

@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.TrafficMessenger")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.TrafficDataProc")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.MapGoogler")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.OrigDestOptimizer")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.TrafficDataMgr")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.datetime")
@mock.patch("traffic_man.traffic_engine.traffic_eng_worker.sleep", return_value = None)
class TestTrafficEngine(TestCase):

    ### --------------------- TrafficEngine.traffic_eng_worker() ----------------------

    def test_traffic_eng_worker_kill_q_not_empty(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, False ]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 0, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)

    def test_traffic_eng_worker_sleep_sec_false(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 59),
                                            datetime(2022, 1, 1, 0, 1, 1)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (False, False)

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 0)

    
    def test_traffic_eng_worker_orig_dest_false(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = False

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 0)
    
    def test_traffic_eng_worker_traffic_cond_false(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = False

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 0)


    def test_traffic_eng_worker_get_orig_dest_list_none(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = None

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.return_value.build_orig_dest_lists.call_count, 0)

    def test_traffic_eng_worker_no_google_maps_raw(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = [[["orig1", "orig2"], 2, [["dest1"], ["dest2"]]]]
        mock_googler.build_orig_dest_lists.return_value = (["orig1", "orig2"], ["dest1", "dest2"])
        mock_googler.return_value.google_call_with_retry.return_value = None

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.build_orig_dest_lists.call_count, 1)
        self.assertEqual(mock_googler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_googler.return_value.calc_traffic.call_count, 0)

    def test_traffic_eng_worker_no_structured_google_data(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = [[["orig1", "orig2"], 2, [["dest1"], ["dest2"]]]]
        mock_googler.build_orig_dest_lists.return_value = (["orig1", "orig2"], ["dest1", "dest2"])
        mock_googler.return_value.google_call_with_retry.return_value =  "fake raw google data"
        mock_googler.calc_traffic.return_value = None
        

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.build_orig_dest_lists.call_count, 1)
        self.assertEqual(mock_googler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_googler.calc_traffic.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.store_traffic_data.call_count, 0)
        self.assertEqual(mock_traff_data_proc.call_count, 0)

    def test_traffic_eng_worker_fail_to_build_dfs(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = [[["orig1", "orig2"], 2, [["dest1"], ["dest2"]]]]
        mock_googler.build_orig_dest_lists.return_value = (["orig1", "orig2"], ["dest1", "dest2"])
        mock_googler.return_value.google_call_with_retry.return_value =  "fake raw google data"
        mock_googler.calc_traffic.return_value = {"fake": "structured data"}
        mock_traff_data_proc.return_value.build_dfs.return_value = None
        

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.build_orig_dest_lists.call_count, 1)
        self.assertEqual(mock_googler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_googler.calc_traffic.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.store_traffic_data.call_count, 1)
        self.assertEqual(mock_traff_data_proc.return_value.get_new_bad_traffic.call_count, 0)

    def test_traffic_eng_worker_fail_bad_and_resolved_traffic_nums(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = [[["orig1", "orig2"], 2, [["dest1"], ["dest2"]]]]
        mock_googler.build_orig_dest_lists.return_value = (["orig1", "orig2"], ["dest1", "dest2"])
        mock_googler.return_value.google_call_with_retry.return_value =  "fake raw google data"
        mock_googler.calc_traffic.return_value = {"fake": "structured data"}
        mock_traff_data_proc.return_value.build_dfs.return_value = True
        mock_traff_data_mgr.proc_bad_traffic_data.return_value = None
        mock_traff_data_mgr.proc_resolved_traffic_data.return_value = None
        

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.build_orig_dest_lists.call_count, 1)
        self.assertEqual(mock_googler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_googler.calc_traffic.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.store_traffic_data.call_count, 1)
        self.assertEqual(mock_traff_data_proc.return_value.get_new_bad_traffic.call_count, 1)
        self.assertEqual(mock_traff_mesgr.send_bad_traffic_sms.call_count, 0)
        self.assertEqual(mock_traff_mesgr.send_resolved_traffic_sms.call_count, 0)

    def test_traffic_eng_worker_full_run(self, mock_sleep, mock_datetime, mock_traff_data_mgr, mock_orig_dest_opt, mock_googler, mock_traff_data_proc, mock_traff_mesgr):
        mock_kill_q = mock.Mock()
        mock_db_req_q = mock.Mock()
        mock_db_res_traff_eng_q = mock.Mock()

        mock_kill_q.empty.side_effect = [True, True, True, True, False]

        mock_datetime.now.side_effect = [
                                            datetime(2022, 1, 1, 0, 0, 0),
                                            datetime(2022, 1, 1, 0, 0, 9),
                                            datetime(2022, 1, 1, 0, 1, 11)
                                        ]
        
        mock_traff_data_mgr.get_next_run.return_value = (10, False)

        mock_traff_data_mgr.get_orig_dest_pairs.return_value = [["orig1", "dest1"],[ "orig2", "dest2"]]
        mock_traff_data_mgr.get_traffic_cond_data.return_value = {"orig1|dest1": "traffic", "orig2|dest2": "traffic_resolved"}
        mock_orig_dest_opt.return_value.get_orig_dest_list.return_value = [[["orig1", "orig2"], 2, [["dest1"], ["dest2"]]]]
        mock_googler.build_orig_dest_lists.return_value = (["orig1", "orig2"], ["dest1", "dest2"])
        mock_googler.return_value.google_call_with_retry.return_value =  "fake raw google data"
        mock_googler.calc_traffic.return_value = {"fake": "structured data"}
        mock_traff_data_proc.return_value.build_dfs.return_value = True
        mock_traff_data_mgr.proc_bad_traffic_data.return_value = ["+12222222222"]
        mock_traff_data_mgr.proc_resolved_traffic_data.return_value = ["+13333333333"]
        

        TrafficEngine.traffic_eng_worker(mock_kill_q, mock_db_req_q, mock_db_res_traff_eng_q)
        self.assertEqual(mock_traff_data_mgr.get_next_run.call_count, 1)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_orig_dest_pairs.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.get_traffic_cond_data.call_count, 1)
        self.assertEqual(mock_orig_dest_opt.call_count, 1)
        self.assertEqual(mock_googler.build_orig_dest_lists.call_count, 1)
        self.assertEqual(mock_googler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_googler.calc_traffic.call_count, 1)
        self.assertEqual(mock_traff_data_mgr.store_traffic_data.call_count, 1)
        self.assertEqual(mock_traff_data_proc.return_value.get_new_bad_traffic.call_count, 1)
        self.assertEqual(mock_traff_mesgr.send_bad_traffic_sms.call_count, 1)
        self.assertEqual(mock_traff_mesgr.send_resolved_traffic_sms.call_count, 1)