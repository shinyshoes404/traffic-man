import unittest, mock
from traffic_man.db.data_setup import DataSetup

class TestDataSetup(unittest.TestCase):

    ### --------------------- DataSetup.update_check_times() ----------------------
    def test_update_check_times_except_on_delete_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app


        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            data_setup = DataSetup(mock_engine)
            check_val = data_setup.update_check_times()
            self.assertIs(check_val, None)
    
    def test_update_check_times_except_on_insert_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.traffic_check_times = ["fake traffic times"]
                with mock.patch("traffic_man.db.data_setup.check_times.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_check_times()
                    self.assertIs(check_val, None)

    def test_update_check_times_success(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, None])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.traffic_check_times = ["fake traffic times"]
                with mock.patch("traffic_man.db.data_setup.check_times.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_check_times()
                    self.assertIs(check_val, True)

    
    ### --------------------- DataSetup.update_holidays() ----------------------
    def test_update_holidays_except_on_delete_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            data_setup = DataSetup(mock_engine)
            check_val = data_setup.update_holidays()
            self.assertIs(check_val, None)

    def test_update_holidays_except_on_insert_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.holidays = ["fake holidays"]
                with mock.patch("traffic_man.db.data_setup.holidays.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_holidays()
                    self.assertIs(check_val, None)

    def test_update_holidays_success(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, None])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.holidays = ["fake holidays"]
                with mock.patch("traffic_man.db.data_setup.holidays.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_holidays()
                    self.assertIs(check_val, True)

    ### --------------------- DataSetup.update_check_days() ----------------------
    def test_update_check_days_except_on_delete_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            data_setup = DataSetup(mock_engine)
            check_val = data_setup.update_check_days()
            self.assertIs(check_val, None)

    def test_update_check_days_except_on_insert_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.traffic_check_days = ["fake traffic days"]
                with mock.patch("traffic_man.db.data_setup.check_days.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_check_days()
                    self.assertIs(check_val, None)

    def test_update_check_days_success(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=[None, None])

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
        with mock.patch("traffic_man.db.data_setup.db.delete") as mock_del:
            with mock.patch("traffic_man.db.data_setup.Config") as mock_config:
                mock_config.traffic_check_days = ["fake holidays"]
                with mock.patch("traffic_man.db.data_setup.check_days.insert") as mock_insert:
                    data_setup = DataSetup(mock_engine)
                    check_val = data_setup.update_check_days()
                    self.assertIs(check_val, True)

# class TestSMSData(unittest.TestCase):

#     ### --------------------- SMSData.check_sms_today() ----------------------
#     def test_check_sms_today_except_on_execute(self):

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception('execute exception'))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.sms_data.select") as mock_select:
#                 test_obj = SMSData(mock_engine)
#                 check_val = test_obj.check_sms_today("traffic")
#                 self.assertIs(check_val, None)

#     def test_check_sms_today_none_sent_yet(self):
#         # define a mock results object
#         mock_results = mock.Mock()
#         mock_results.fetchall.return_value = []

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_results)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.sms_data.select") as mock_select:
#                 test_obj = SMSData(mock_engine)
#                 check_val = test_obj.check_sms_today("traffic")
#                 self.assertIs(check_val, False)

#     def test_check_sms_today_msg_sent_today(self):
#         # define a mock results object
#         mock_results = mock.Mock()
#         mock_results.fetchall.return_value = [(1, '2022-10-22', 'traffic', 0)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_results)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.sms_data.select") as mock_select:
#                 test_obj = SMSData(mock_engine)
#                 check_val = test_obj.check_sms_today("traffic")
#                 self.assertIs(check_val, True)

#     ### --------------------- SMSData.write_sms_record() ----------------------
#     def test_write_sms_record_except_on_execute(self):

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception('execute exception'))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.sms_data.insert") as mock_select:
#                 test_obj = SMSData(mock_engine)
#                 check_val = test_obj.write_sms_record("traffic", 0)
#                 self.assertIs(check_val, None)

#     def test_write_sms_record_success(self):

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(mock.Mock())

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.sms_data.insert") as mock_select:
#                 test_obj = SMSData(mock_engine)
#                 check_val = test_obj.write_sms_record("traffic", 0)
#                 self.assertIs(check_val, True)

