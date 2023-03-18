from unittest import TestCase, mock
from traffic_man.sms_processor.sms_data_manager import SMSDataMgr
from traffic_man.db.db_worker import db_worker
from traffic_man.config import Config
import threading, queue, os, sqlite3


@mock.patch("traffic_man.db.db_worker.Config.db_path", new_callable=mock.PropertyMock)
class TestSMSDataMgr_SetUserByPhoneNumber(TestCase):
    test_db_location = os.path.join(Config.etc_basedir, "test_db.db")

    def tearDown(self):
        if os.path.exists(self.test_db_location):
            os.remove(self.test_db_location)
        

    def test_int_set_user_by_phone_number_successful_insert(self, mock_db_path):
        mock_db_path.return_value = '' # run in memory db
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_insert_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, phone_num, 'sub', 'auth', 'origin1', 'dest1')
        user_data = sms_data_mgr.get_user_by_phone_num(phone_num, db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        self.assertIs(test_insert_result, True)
        self.assertEqual(user_data["phone_num"], phone_num)
        self.assertEqual(user_data["status"], "sub")
        self.assertEqual(user_data["auth_status"], "auth")
        self.assertEqual(user_data["origin_place_id"], "origin1")
        self.assertEqual(user_data["dest_place_id"], "dest1")

    def test_int_set_user_by_phone_number_successful_insert_update(self, mock_db_path):
        mock_db_path.return_value = '' # run in memory db
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_insert_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, phone_num, 'sub', 'auth', 'origin1', 'dest1')
        test_update_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, False, phone_num, 'unsub', 'not auth')

        user_data = sms_data_mgr.get_user_by_phone_num(phone_num, db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        self.assertIs(test_insert_result, True)
        self.assertIs(test_update_result, True)
        self.assertEqual(user_data["phone_num"], phone_num)
        self.assertEqual(user_data["status"], "unsub")
        self.assertEqual(user_data["auth_status"], "not auth")
        self.assertEqual(user_data["origin_place_id"], "origin1")
        self.assertEqual(user_data["dest_place_id"], "dest1")

    def test_int_set_user_by_phone_number_fail_update(self, mock_db_path):
        mock_db_path.return_value = '' # run in memory db
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_insert_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, phone_num, 'sub', 'auth', 'origin1', 'dest1')
        test_update_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, False, phone_num, ['bad', 'data', 1], 'not auth')

        user_data = sms_data_mgr.get_user_by_phone_num(phone_num, db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        self.assertIs(test_insert_result, True)
        self.assertIs(test_update_result, None)
        self.assertEqual(user_data["phone_num"], phone_num)
        self.assertEqual(user_data["status"], "sub")
        self.assertEqual(user_data["auth_status"], "auth")
        self.assertEqual(user_data["origin_place_id"], "origin1")
        self.assertEqual(user_data["dest_place_id"], "dest1")

    def test_int_set_user_by_phone_number_fail_insert(self, mock_db_path):
        mock_db_path.return_value = '' # run in memory db
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_insert_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, None, 'sub', 'auth', 'origin1', 'dest1')
        user_data = sms_data_mgr.get_user_by_phone_num(phone_num, db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        self.assertIs(test_insert_result, None)
        self.assertIs(user_data, None)

    def test_int_set_user_by_phone_number_fail_get(self, mock_db_path):
        mock_db_path.return_value = '' # run in memory db
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_insert_result = sms_data_mgr.set_user_by_phone_num(db_req_q, db_res_sms_q, True, phone_num, 'sub', 'auth', 'origin1', 'dest1')
        user_data = sms_data_mgr.get_user_by_phone_num(["list", 2, "bad data"], db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        self.assertIs(test_insert_result, True)
        self.assertIs(user_data, False)


    def test_int_log_sms_msg_successful(self, mock_db_path):
        mock_db_path.return_value = self.test_db_location # storing as a file to access later for testing
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_result = sms_data_mgr.log_sms_msg(phone_num, "some message", "some msg type", "some status", "2022-01-04 03:21:10", "outbound", db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        # verify data in test db file
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()
        cur.execute("SELECT * FROM sms_data;")
        rows = cur.fetchall()
        cur.close()
        conn.close()


        self.assertEqual(test_result, 0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "some msg type")

    def test_int_log_sms_msg_fail(self, mock_db_path):
        mock_db_path.return_value = self.test_db_location # storing as a file to access later for testing
        kill_q = queue.Queue()
        db_req_q = queue.Queue()
        db_res_sms_q = queue.Queue()
        db_res_traffic_eng_q = queue.Queue()

        db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
        db_engine_thread.start()
  
        sms_data_mgr = SMSDataMgr()
        phone_num = '+15554443333'
        test_result = sms_data_mgr.log_sms_msg(phone_num, ["bad", "data"], "some msg type", "some status", "2022-01-04 03:21:10", "outbound", db_req_q, db_res_sms_q)

        kill_q.put("kill")
        db_engine_thread.join()

        # verify data in test db file
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()
        cur.execute("SELECT * FROM sms_data;")
        rows = cur.fetchall()
        cur.close()
        conn.close()


        self.assertEqual(test_result, 1)
        self.assertEqual(len(rows), 0)

    
