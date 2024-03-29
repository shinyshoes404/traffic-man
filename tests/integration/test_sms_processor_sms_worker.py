from unittest import TestCase, mock
from importlib import reload
from traffic_man.sms_processor.sms_worker import SMSWorker
from traffic_man.db.db_worker import db_worker
from traffic_man.config import Config
from time import sleep
import logging
import threading, queue, os, sqlite3, re, uuid

logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)


        
@mock.patch("traffic_man.sms_processor.sms_worker.PlaceFinder")
@mock.patch.dict(os.environ, {"TRAFFIC_MAN_CODE": "my secret phrase"})
@mock.patch("traffic_man.sms_processor.sms_worker.TwilioSender")
@mock.patch("traffic_man.db.db_worker.Config.db_path", new_callable=mock.PropertyMock)
class TestSMSWorker(TestCase):

    test_db_location = os.path.join(Config.etc_basedir, "test_db.db")

    def util_test_engine(self, sms_obj_list: list[dict]) -> None:

            kill_q = queue.Queue()
            db_req_q = queue.Queue()
            db_res_sms_q = queue.Queue()
            db_res_traffic_eng_q = queue.Queue()
            inbound_sms_q = queue.Queue()

            db_engine_thread = threading.Thread(name="db-engine", target=db_worker, args=[kill_q, db_req_q, db_res_traffic_eng_q, db_res_sms_q])
            db_engine_thread.start()
            sleep(0.75)

            sms_proc_thread = threading.Thread(name="sms-proc", target=SMSWorker.sms_worker, args=[kill_q, db_req_q, db_res_sms_q, inbound_sms_q])
            sms_proc_thread.start()

            for sms_obj in sms_obj_list:
                inbound_sms_q.put(sms_obj)
                logger.debug(sms_obj)

            sleep(1.75) # let everything work through the system

            kill_q.put("kill") # stop all threads

            # collect our threads before moving on
            db_engine_thread.join()
            sms_proc_thread.join()


    def util_check_log_for_errors(self, test_id) -> bool:
            with open(Config.log_path, 'r') as file:
                log_content = file.read()
            
            sub_log = re.search(test_id + '-START(.*)' + test_id + '-END', log_content, re.DOTALL)
            return sub_log.group(1).count('[ERROR]')
               

    def setUp(self):
        if os.path.exists(self.test_db_location):
            os.remove(self.test_db_location)


    def tearDown(self):
        if os.path.exists(self.test_db_location):
            os.remove(self.test_db_location)
    

    def test_int_invalid_phone_number(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location

        sms_object = {
            "Body": "fake sms message body",
            "From": "+35923333333",
            "received_datetime": "2023-01-11 04:27:42"
        }

        self.util_test_engine([sms_object])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 1)
        self.assertEqual(sms_rows[0][1], sms_object["received_datetime"])
        self.assertEqual(sms_rows[0][2], "invalid")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object["Body"])
        self.assertEqual(sms_rows[0][6], sms_object["From"][:12])

        self.assertEqual(len(phone_num_rows), 0)
        

    def test_int_sub_new_user(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location
        mock_twilio_sender.return_value.send_need_auth_sms.return_value = (True, "test sms body")

        sms_object = {
            "Body": "start",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        self.util_test_engine([sms_object])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 2)
        self.assertEqual(sms_rows[0][1], sms_object["received_datetime"])
        self.assertEqual(sms_rows[0][2], "subscribe")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object["Body"])
        self.assertEqual(sms_rows[0][6], sms_object["From"][:12])

        self.assertEqual(sms_rows[1][2], "auth needed")
        self.assertEqual(sms_rows[1][3], "sent")
        self.assertEqual(sms_rows[1][4], "outbound")
        self.assertEqual(sms_rows[1][5], "test sms body")
        self.assertEqual(sms_rows[1][6], sms_object["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object["From"])
        self.assertEqual(phone_num_rows[0][3], "needs setup")
        self.assertEqual(phone_num_rows[0][4], "not auth")


    def test_int_new_user_successful_auth(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location
        mock_twilio_sender.return_value.send_auth_success_sms.return_value = (True, "test sms body")

        sms_object = {
            "Body": " My  secrEt Phrase  ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        self.util_test_engine([sms_object])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 2)
        self.assertEqual(sms_rows[0][1], sms_object["received_datetime"])
        self.assertEqual(sms_rows[0][2], "general")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object["Body"])
        self.assertEqual(sms_rows[0][6], sms_object["From"][:12])

        self.assertEqual(sms_rows[1][2], "auth success")
        self.assertEqual(sms_rows[1][3], "sent")
        self.assertEqual(sms_rows[1][4], "outbound")
        self.assertEqual(sms_rows[1][5], "test sms body")
        self.assertEqual(sms_rows[1][6], sms_object["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object["From"])
        self.assertEqual(phone_num_rows[0][3], "needs setup")
        self.assertEqual(phone_num_rows[0][4], "auth")


    def test_int_new_sub_existing_successful_auth(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location
        mock_twilio_sender.return_value.send_need_auth_sms.return_value = (True, "test need auth sms body")
        mock_twilio_sender.return_value.send_auth_success_sms.return_value = (True, "test auth success sms body")

        sms_object_1 = {
            "Body": " sTaRt ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        sms_object_2 = {
            "Body": " My  secrEt Phrase  ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:50"
        }

        self.util_test_engine([sms_object_1, sms_object_2])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 4)

        self.assertEqual(sms_rows[0][1], sms_object_1["received_datetime"])
        self.assertEqual(sms_rows[0][2], "subscribe")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object_1["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[1][2], "auth needed")
        self.assertEqual(sms_rows[1][3], "sent")
        self.assertEqual(sms_rows[1][4], "outbound")
        self.assertEqual(sms_rows[1][5], "test need auth sms body")
        self.assertEqual(sms_rows[1][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[2][1], sms_object_2["received_datetime"])
        self.assertEqual(sms_rows[2][2], "general")
        self.assertEqual(sms_rows[2][3], "received")
        self.assertEqual(sms_rows[2][4], "inbound")
        self.assertEqual(sms_rows[2][5], sms_object_2["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_2["From"][:12])

        self.assertEqual(sms_rows[3][2], "auth success")
        self.assertEqual(sms_rows[3][3], "sent")
        self.assertEqual(sms_rows[3][4], "outbound")
        self.assertEqual(sms_rows[3][5], "test auth success sms body")
        self.assertEqual(sms_rows[3][6], sms_object_1["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object_1["From"])
        self.assertEqual(phone_num_rows[0][3], "needs setup")
        self.assertEqual(phone_num_rows[0][4], "auth")



    def test_int_new_unsub_existing_unsub(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location
       
        sms_object_1 = {
            "Body": " St o P ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        sms_object_2 = {
            "Body": "c An cel",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:50"
        }

        self.util_test_engine([sms_object_1, sms_object_2])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 2)

        self.assertEqual(sms_rows[0][1], sms_object_1["received_datetime"])
        self.assertEqual(sms_rows[0][2], "unsubscribe")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object_1["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[1][1], sms_object_2["received_datetime"])
        self.assertEqual(sms_rows[1][2], "unsubscribe")
        self.assertEqual(sms_rows[1][3], "received")
        self.assertEqual(sms_rows[1][4], "inbound")
        self.assertEqual(sms_rows[1][5], sms_object_2["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_2["From"][:12])


        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object_1["From"])
        self.assertEqual(phone_num_rows[0][3], "unsub")
        self.assertEqual(phone_num_rows[0][4], "not auth")


    def test_int_new_info_not_auth_existing_auth_sucess_existing_info_existing_needs_setup_existing_info(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location
        mock_twilio_sender.return_value.send_auth_success_sms.return_value = (True, "test auth success sms body")
        mock_twilio_sender.return_value.send_need_auth_sms.return_value = (True, "test needs auth")
        mock_twilio_sender.return_value.send_needs_setup_sms.return_value = (True, "test needs setup")
        mock_twilio_sender.return_value.send_user_info_sms.return_value = (True, "test user info")


        sms_object_1 = {
            "Body": " i n F o  ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:50"
        }

        sms_object_2 = {
            "Body": "My  secrEt PhrasE",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        sms_object_3 = {
            "Body": " i n F o  ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:50"
        }



        self.util_test_engine([sms_object_1, sms_object_2, sms_object_3])


        # manually update user data
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("UPDATE phone_numbers SET origin_place_id = 'orig1', dest_place_id = 'dest1', status = 'sub' WHERE phone_num = '+12223334444';")
        conn.commit()
        cur.close()
        conn.close() 

        # simulate another inbound sms
        sms_object_4 = {
            "Body": "help",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:55"
        }

        self.util_test_engine([sms_object_4])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()


        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 8)

        self.assertEqual(sms_rows[0][1], sms_object_1["received_datetime"])
        self.assertEqual(sms_rows[0][2], "info")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object_1["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[1][2], "auth needed")
        self.assertEqual(sms_rows[1][3], "sent")
        self.assertEqual(sms_rows[1][4], "outbound")
        self.assertEqual(sms_rows[1][5], "test needs auth")
        self.assertEqual(sms_rows[1][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[2][1], sms_object_2["received_datetime"])
        self.assertEqual(sms_rows[2][2], "general")
        self.assertEqual(sms_rows[2][3], "received")
        self.assertEqual(sms_rows[2][4], "inbound")
        self.assertEqual(sms_rows[2][5], sms_object_2["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_2["From"][:12])

        self.assertEqual(sms_rows[3][2], "auth success")
        self.assertEqual(sms_rows[3][3], "sent")
        self.assertEqual(sms_rows[3][4], "outbound")
        self.assertEqual(sms_rows[3][5], "test auth success sms body")
        self.assertEqual(sms_rows[3][6], sms_object_2["From"][:12])

        self.assertEqual(sms_rows[4][1], sms_object_3["received_datetime"])
        self.assertEqual(sms_rows[4][2], "info")
        self.assertEqual(sms_rows[4][3], "received")
        self.assertEqual(sms_rows[4][4], "inbound")
        self.assertEqual(sms_rows[4][5], sms_object_3["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_3["From"][:12])

        self.assertEqual(sms_rows[5][2], "needs setup")
        self.assertEqual(sms_rows[5][3], "sent")
        self.assertEqual(sms_rows[5][4], "outbound")
        self.assertEqual(sms_rows[5][5], "test needs setup")
        self.assertEqual(sms_rows[5][6], sms_object_3["From"][:12])

        self.assertEqual(sms_rows[6][1], sms_object_4["received_datetime"])
        self.assertEqual(sms_rows[6][2], "info")
        self.assertEqual(sms_rows[6][3], "received")
        self.assertEqual(sms_rows[6][4], "inbound")
        self.assertEqual(sms_rows[6][5], sms_object_4["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_4["From"][:12])

        self.assertEqual(sms_rows[7][2], "info")
        self.assertEqual(sms_rows[7][3], "sent")
        self.assertEqual(sms_rows[7][4], "outbound")
        self.assertEqual(sms_rows[7][5], "test user info")
        self.assertEqual(sms_rows[7][6], sms_object_4["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object_1["From"])
        self.assertEqual(phone_num_rows[0][3], "sub")
        self.assertEqual(phone_num_rows[0][4], "auth")


    def test_int_new_unsub_existing_info_existing_auth_existing_sub(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location    
        mock_twilio_sender.return_value.send_needs_setup_sms.return_value = (True, "test needs setup")
        mock_twilio_sender.return_value.send_sub_sms.return_value = (True, "test sub")

        sms_object_1 = {
            "Body": "sT op",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:40"
        }

        sms_object_2 = {
            "Body": "helP",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:41"
        }
        sms_object_3 = {
            "Body": "My  secrEt PhrasE",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        sms_object_4 = {
            "Body": "s t ART ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:43"
        }



        self.util_test_engine([sms_object_1, sms_object_2, sms_object_3, sms_object_4])

        # manually update user data
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("UPDATE phone_numbers SET origin_place_id = 'orig1', dest_place_id = 'dest1' WHERE phone_num = '+12223334444';")
        conn.commit()
        cur.close()
        conn.close() 

        sms_object_5 = {
            "Body": "s t ART ",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:44"
        }

        self.util_test_engine([sms_object_5])

        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 0)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()

        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 7)

        self.assertEqual(sms_rows[0][1], sms_object_1["received_datetime"])
        self.assertEqual(sms_rows[0][2], "unsubscribe")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object_1["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[1][1], sms_object_2["received_datetime"])
        self.assertEqual(sms_rows[1][2], "info")
        self.assertEqual(sms_rows[1][3], "received")
        self.assertEqual(sms_rows[1][4], "inbound")
        self.assertEqual(sms_rows[1][5], sms_object_2["Body"])
        self.assertEqual(sms_rows[1][6], sms_object_2["From"][:12])

        self.assertEqual(sms_rows[2][1], sms_object_3["received_datetime"])
        self.assertEqual(sms_rows[2][2], "general")
        self.assertEqual(sms_rows[2][3], "received")
        self.assertEqual(sms_rows[2][4], "inbound")
        self.assertEqual(sms_rows[2][5], sms_object_3["Body"])
        self.assertEqual(sms_rows[2][6], sms_object_3["From"][:12])

        self.assertEqual(sms_rows[3][1], sms_object_4["received_datetime"])
        self.assertEqual(sms_rows[3][2], "subscribe")
        self.assertEqual(sms_rows[3][3], "received")
        self.assertEqual(sms_rows[3][4], "inbound")
        self.assertEqual(sms_rows[3][5], sms_object_4["Body"])
        self.assertEqual(sms_rows[3][6], sms_object_4["From"][:12])

        self.assertEqual(sms_rows[4][2], "needs setup")
        self.assertEqual(sms_rows[4][3], "sent")
        self.assertEqual(sms_rows[4][4], "outbound")
        self.assertEqual(sms_rows[4][5], "test needs setup")
        self.assertEqual(sms_rows[4][6], sms_object_4["From"][:12])

        self.assertEqual(sms_rows[5][1], sms_object_5["received_datetime"])
        self.assertEqual(sms_rows[5][2], "subscribe")
        self.assertEqual(sms_rows[5][3], "received")
        self.assertEqual(sms_rows[5][4], "inbound")
        self.assertEqual(sms_rows[5][5], sms_object_5["Body"])
        self.assertEqual(sms_rows[5][6], sms_object_5["From"][:12])

        self.assertEqual(sms_rows[6][2], "needs setup")
        self.assertEqual(sms_rows[6][3], "sent")
        self.assertEqual(sms_rows[6][4], "outbound")
        self.assertEqual(sms_rows[6][5], "test needs setup")
        self.assertEqual(sms_rows[6][6], sms_object_5["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object_1["From"])
        self.assertEqual(phone_num_rows[0][3], "needs setup")
        self.assertEqual(phone_num_rows[0][4], "auth")



    def test_int_new_sub_failauth_authsuccess_origsearch_origconfirm_errorsearch_searchdest_destconfirm_sub(self, mock_db_path, mock_twilio_sender, mock_place_finder):
        test_id = str(uuid.uuid4())
        logger.info(test_id + "-START")
        mock_db_path.return_value = self.test_db_location    
        mock_twilio_sender.return_value.send_needs_setup_sms.return_value = (True, "test needs setup")
        mock_twilio_sender.return_value.send_auth_success_sms.return_value = (True, "test auth success")
        mock_twilio_sender.return_value.send_user_info_sms.return_value = (True, "test info")
        mock_twilio_sender.return_value.send_need_auth_sms.return_value = (True, "test need auth")
        mock_twilio_sender.return_value.send_no_results_sms.return_value = (True, "test no results")
        mock_twilio_sender.return_value.send_service_error_sms.return_value = (True, "test svc error")
        mock_twilio_sender.return_value.send_addr_check.return_value = (True, "test addr check")
        mock_twilio_sender.return_value.send_sub_sms.return_value = (True, "test sub")

        mock_place_finder.return_value.search_for_place_id.side_effect = [
            { "search_status": "ok", "msg": "found results", "addr": "wrong addr 1", "place_id": "wrong1", "results_count": 1},
            { "search_status": "ok", "msg": "found results", "addr": "100 N Main St, Anywhere, ST, USA", "place_id": "orig1", "results_count": 1},
            { "search_status": "api error", "msg": "encountered an error with the api", "addr": None, "place_id": None, "results_count": 0},
            { "search_status": "no results", "msg": "no results returned for search", "addr": None, "place_id": None, "results_count": 0},
            { "search_status": "ok", "msg": "found results", "addr": "wrong addr 2", "place_id": "wrong2", "results_count": 1},
            { "search_status": "ok", "msg": "found results", "addr": "101 N Main St, Anywhere, ST, USA", "place_id": "dest1", "results_count": 1}
        ]

        sms_object_1 = {
            "Body": "start",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:40"
        }

        sms_object_2 = {
            "Body": "random sms 1",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:41"
        }
        
        sms_object_3 = {
            "Body": "My  secrEt PhrasE",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:42"
        }

        sms_object_4 = {
            "Body": "addr search origin 1",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:43"
        }


        sms_object_5 = {
            "Body": "addr search origin 2",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:43"
        }

        sms_object_6 = {
            "Body": "CORRECT",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:44"
        }

        sms_object_7 = {
            "Body": "bad search",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:45"
        }

        sms_object_8 = {
            "Body": "error search",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:46"
        }

        sms_object_9 = {
            "Body": "addr search dest 1",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:47"
        }

        sms_object_10 = {
            "Body": "addr search dest 2",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:47"
        }

        sms_object_11 = {
            "Body": "CORRECT",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:48"
        }

        sms_object_12 = {
            "Body": "start",
            "From": "+12223334444",
            "received_datetime": "2023-01-11 04:27:49"
        }

        self.util_test_engine([sms_object_1, 
                               sms_object_2, 
                               sms_object_3, 
                               sms_object_4, 
                               sms_object_5, 
                               sms_object_6, 
                               sms_object_7, 
                               sms_object_8, 
                               sms_object_9,
                               sms_object_10,
                               sms_object_11,
                               sms_object_12
                               ])


        logger.info(test_id + "-END")


        # check test log file for errors
        log_error = self.util_check_log_for_errors(test_id)
        self.assertEqual(log_error, 1)

        # check the data in the db
        conn = sqlite3.connect(self.test_db_location)
        cur = conn.cursor()

        cur.execute("SELECT * FROM sms_data;")
        sms_rows = cur.fetchall()
        logger.debug("sms rows: \n{0}".format(sms_rows))

        cur.execute("SELECT * FROM phone_numbers;")
        phone_num_rows = cur.fetchall()

        cur.close()
        conn.close() 

        self.assertEqual(len(sms_rows), 24)

        self.assertEqual(sms_rows[0][1], sms_object_1["received_datetime"])
        self.assertEqual(sms_rows[0][2], "subscribe")
        self.assertEqual(sms_rows[0][3], "received")
        self.assertEqual(sms_rows[0][4], "inbound")
        self.assertEqual(sms_rows[0][5], sms_object_1["Body"])
        self.assertAlmostEqual(sms_rows[0][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[1][2], "auth needed")
        self.assertEqual(sms_rows[1][3], "sent")
        self.assertEqual(sms_rows[1][4], "outbound")
        self.assertEqual(sms_rows[1][5], "test need auth")
        self.assertEqual(sms_rows[1][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[2][1], sms_object_2["received_datetime"])
        self.assertEqual(sms_rows[2][2], "general")
        self.assertEqual(sms_rows[2][3], "received")
        self.assertEqual(sms_rows[2][4], "inbound")
        self.assertEqual(sms_rows[2][5], sms_object_2["Body"])
        self.assertEqual(sms_rows[2][6], sms_object_2["From"][:12])

        self.assertEqual(sms_rows[3][2], "auth needed")
        self.assertEqual(sms_rows[3][3], "sent")
        self.assertEqual(sms_rows[3][4], "outbound")
        self.assertEqual(sms_rows[3][5], "test need auth")
        self.assertEqual(sms_rows[3][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[4][1], sms_object_3["received_datetime"])
        self.assertEqual(sms_rows[4][2], "general")
        self.assertEqual(sms_rows[4][3], "received")
        self.assertEqual(sms_rows[4][4], "inbound")
        self.assertEqual(sms_rows[4][5], sms_object_3["Body"])
        self.assertEqual(sms_rows[4][6], sms_object_3["From"][:12])

        self.assertEqual(sms_rows[5][2], "auth success")
        self.assertEqual(sms_rows[5][3], "sent")
        self.assertEqual(sms_rows[5][4], "outbound")
        self.assertEqual(sms_rows[5][5], "test auth success")
        self.assertEqual(sms_rows[5][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[6][1], sms_object_4["received_datetime"])
        self.assertEqual(sms_rows[6][2], "general")
        self.assertEqual(sms_rows[6][3], "received")
        self.assertEqual(sms_rows[6][4], "inbound")
        self.assertEqual(sms_rows[6][5], sms_object_4["Body"])
        self.assertEqual(sms_rows[6][6], sms_object_4["From"][:12])

        self.assertEqual(sms_rows[7][2], "addr check")
        self.assertEqual(sms_rows[7][3], "sent")
        self.assertEqual(sms_rows[7][4], "outbound")
        self.assertEqual(sms_rows[7][5], "test addr check")
        self.assertEqual(sms_rows[7][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[8][1], sms_object_5["received_datetime"])
        self.assertEqual(sms_rows[8][2], "general")
        self.assertEqual(sms_rows[8][3], "received")
        self.assertEqual(sms_rows[8][4], "inbound")
        self.assertEqual(sms_rows[8][5], sms_object_5["Body"])
        self.assertEqual(sms_rows[8][6], sms_object_5["From"][:12])

        self.assertEqual(sms_rows[9][2], "addr check")
        self.assertEqual(sms_rows[9][3], "sent")
        self.assertEqual(sms_rows[9][4], "outbound")
        self.assertEqual(sms_rows[9][5], "test addr check")
        self.assertEqual(sms_rows[9][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[10][1], sms_object_6["received_datetime"])
        self.assertEqual(sms_rows[10][2], "general")
        self.assertEqual(sms_rows[10][3], "received")
        self.assertEqual(sms_rows[10][4], "inbound")
        self.assertEqual(sms_rows[10][5], sms_object_6["Body"])
        self.assertEqual(sms_rows[10][6], sms_object_6["From"][:12])

        self.assertEqual(sms_rows[11][2], "needs setup")
        self.assertEqual(sms_rows[11][3], "sent")
        self.assertEqual(sms_rows[11][4], "outbound")
        self.assertEqual(sms_rows[11][5], "test needs setup")
        self.assertEqual(sms_rows[11][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[12][1], sms_object_7["received_datetime"])
        self.assertEqual(sms_rows[12][2], "general")
        self.assertEqual(sms_rows[12][3], "received")
        self.assertEqual(sms_rows[12][4], "inbound")
        self.assertEqual(sms_rows[12][5], sms_object_7["Body"])
        self.assertEqual(sms_rows[12][6], sms_object_7["From"][:12])

        self.assertEqual(sms_rows[13][2], "service error")
        self.assertEqual(sms_rows[13][3], "sent")
        self.assertEqual(sms_rows[13][4], "outbound")
        self.assertEqual(sms_rows[13][5], "test svc error")
        self.assertEqual(sms_rows[13][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[14][1], sms_object_8["received_datetime"])
        self.assertEqual(sms_rows[14][2], "general")
        self.assertEqual(sms_rows[14][3], "received")
        self.assertEqual(sms_rows[14][4], "inbound")
        self.assertEqual(sms_rows[14][5], sms_object_8["Body"])
        self.assertEqual(sms_rows[14][6], sms_object_8["From"][:12])

        self.assertEqual(sms_rows[15][2], "no results")
        self.assertEqual(sms_rows[15][3], "sent")
        self.assertEqual(sms_rows[15][4], "outbound")
        self.assertEqual(sms_rows[15][5], "test no results")
        self.assertEqual(sms_rows[15][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[16][1], sms_object_9["received_datetime"])
        self.assertEqual(sms_rows[16][2], "general")
        self.assertEqual(sms_rows[16][3], "received")
        self.assertEqual(sms_rows[16][4], "inbound")
        self.assertEqual(sms_rows[16][5], sms_object_9["Body"])
        self.assertEqual(sms_rows[16][6], sms_object_9["From"][:12])

        self.assertEqual(sms_rows[17][2], "addr check")
        self.assertEqual(sms_rows[17][3], "sent")
        self.assertEqual(sms_rows[17][4], "outbound")
        self.assertEqual(sms_rows[17][5], "test addr check")
        self.assertEqual(sms_rows[17][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[18][1], sms_object_10["received_datetime"])
        self.assertEqual(sms_rows[18][2], "general")
        self.assertEqual(sms_rows[18][3], "received")
        self.assertEqual(sms_rows[18][4], "inbound")
        self.assertEqual(sms_rows[18][5], sms_object_10["Body"])
        self.assertEqual(sms_rows[18][6], sms_object_10["From"][:12])

        self.assertEqual(sms_rows[19][2], "addr check")
        self.assertEqual(sms_rows[19][3], "sent")
        self.assertEqual(sms_rows[19][4], "outbound")
        self.assertEqual(sms_rows[19][5], "test addr check")
        self.assertEqual(sms_rows[19][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[20][1], sms_object_11["received_datetime"])
        self.assertEqual(sms_rows[20][2], "general")
        self.assertEqual(sms_rows[20][3], "received")
        self.assertEqual(sms_rows[20][4], "inbound")
        self.assertEqual(sms_rows[20][5], sms_object_11["Body"])
        self.assertEqual(sms_rows[20][6], sms_object_11["From"][:12])

        self.assertEqual(sms_rows[21][2], "info")
        self.assertEqual(sms_rows[21][3], "sent")
        self.assertEqual(sms_rows[21][4], "outbound")
        self.assertEqual(sms_rows[21][5], "test info")
        self.assertEqual(sms_rows[21][6], sms_object_1["From"][:12])

        self.assertEqual(sms_rows[22][1], sms_object_12["received_datetime"])
        self.assertEqual(sms_rows[22][2], "subscribe")
        self.assertEqual(sms_rows[22][3], "received")
        self.assertEqual(sms_rows[22][4], "inbound")
        self.assertEqual(sms_rows[22][5], sms_object_12["Body"])
        self.assertEqual(sms_rows[22][6], sms_object_12["From"][:12])

        self.assertEqual(sms_rows[23][2], "subscribe")
        self.assertEqual(sms_rows[23][3], "sent")
        self.assertEqual(sms_rows[23][4], "outbound")
        self.assertEqual(sms_rows[23][5], "test sub")
        self.assertEqual(sms_rows[23][6], sms_object_1["From"][:12])

        self.assertEqual(len(phone_num_rows), 1)
        self.assertEqual(phone_num_rows[0][0], sms_object_1["From"])
        self.assertEqual(phone_num_rows[0][1], "orig1")
        self.assertEqual(phone_num_rows[0][2], "dest1")        
        self.assertEqual(phone_num_rows[0][3], "sub")
        self.assertEqual(phone_num_rows[0][4], "auth")
        self.assertEqual(phone_num_rows[0][5], "yes")
        self.assertEqual(phone_num_rows[0][6], "yes")              