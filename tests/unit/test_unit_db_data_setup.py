import unittest, mock, os, datetime
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

    
#     ### --------------------- DataSetup.update_holidays() ----------------------
#     def test_update_holidays_except_on_delete_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             data_setup = DataSetup(mock_engine)
#             check_val = data_setup.update_holidays()
#             self.assertIs(check_val, None)

#     def test_update_holidays_except_on_insert_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.Config") as mock_config:
#                 mock_config.holidays = ["fake holidays"]
#                 with mock.patch("traffic_man.db_ops.holidays.insert") as mock_insert:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_holidays()
#                     self.assertIs(check_val, None)

#     def test_update_holidays_success(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, None])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.Config") as mock_config:
#                 mock_config.holidays = ["fake holidays"]
#                 with mock.patch("traffic_man.db_ops.holidays.insert") as mock_insert:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_holidays()
#                     self.assertIs(check_val, True)

#     ### --------------------- DataSetup.update_check_days() ----------------------
#     def test_update_check_days_except_on_delete_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             data_setup = DataSetup(mock_engine)
#             check_val = data_setup.update_check_days()
#             self.assertIs(check_val, None)

#     def test_update_check_days_except_on_insert_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.Config") as mock_config:
#                 mock_config.traffic_check_days = ["fake traffic days"]
#                 with mock.patch("traffic_man.db_ops.check_days.insert") as mock_insert:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_check_days()
#                     self.assertIs(check_val, None)

#     def test_update_check_days_success(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, None])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.Config") as mock_config:
#                 mock_config.traffic_check_days = ["fake holidays"]
#                 with mock.patch("traffic_man.db_ops.check_days.insert") as mock_insert:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_check_days()
#                     self.assertIs(check_val, True)


#     ### --------------------- DataSetup.update_phone_numbers() ----------------------
#     def test_update_phone_numbers_except_on_delete_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("del execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             data_setup = DataSetup(mock_engine)
#             check_val = data_setup.update_phone_numbers()
#             self.assertIs(check_val, None)

#     def test_update_phone_numbers_except_on_insert_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, Exception("insert execute exception")])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.check_days.insert") as mock_insert:
#                 with mock.patch.dict(os.environ, {"PHONE_NUMS":"+15555555555|+13333333333"}, clear=True ) as mock_env:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_phone_numbers()
#                     self.assertIs(check_val, None)

#     def test_update_phone_numbers_success(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=[None, None, None])

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app
        
#         with mock.patch("traffic_man.db_ops.db.delete") as mock_del:
#             with mock.patch("traffic_man.db_ops.check_days.insert") as mock_insert:
#                 with mock.patch.dict(os.environ, {"PHONE_NUMS":"+15555555555|+13333333333"}, clear=True ) as mock_env:
#                     data_setup = DataSetup(mock_engine)
#                     check_val = data_setup.update_phone_numbers()
#                     self.assertIs(check_val, True)
#                     self.assertEqual(mock_conn.execute.call_count, 3)


# class TestTrafficDateTime(unittest.TestCase):

#     ### --------------------- TrafficDateTime._get_1201_tomorrow() ----------------------
#     def test_get_1201_tomorrow(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             test_obj = TrafficDateTime()
#             test_obj.curr_date = "2022-10-22"
#             self.assertEqual(datetime.datetime(2022, 10, 23, 0, 1), test_obj._get_1201_tomorrow())

#     ### --------------------- TrafficDateTime._check_weekday() ----------------------
#     def test_check_weekday_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.check_days.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_weekday = "wednesday"
#             check_val = test_obj._check_weekday()
#             self.assertIs(check_val, None)
        
#     def test_check_weekday_not_a_traffic_check_day(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = []

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.check_days.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_weekday = "sunday"
#             check_val = test_obj._check_weekday()
#             self.assertIs(check_val, False)

#     def test_check_weekday_traffic_check_day(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = [("monday",)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.check_days.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_weekday = "monday"
#             check_val = test_obj._check_weekday()
#             self.assertIs(check_val, True)


#     ### --------------------- TrafficDateTime._check_holiday() ----------------------
#     def test_check_holiday_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.holidays.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_date = "2022-07-05"
#             check_val = test_obj._check_holiday()
#             self.assertIs(check_val, None)
        
#     def test_check_holiday_not_a_holiday(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = []

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.holidays.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_date = "2022-07-05"
#             check_val = test_obj._check_holiday()
#             self.assertIs(check_val, False)

#     def test_check_holiday_is_holiday(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = [("2022-07-04",)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.holidays.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_date = "2022-07-04"
#             check_val = test_obj._check_holiday()
#             self.assertIs(check_val, True)

#     ### --------------------- TrafficDateTime._get_seconds_to_time() ----------------------
#     def test_get_seconds_to_time(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             test_obj = TrafficDateTime()
#             test_obj.curr_date = "2022-10-22"
#             test_obj.curr_datetime = datetime.datetime(2022, 10, 22, 0, 0, 0)
#             check_val = test_obj._get_seconds_to_time("00:01")
#             self.assertEqual(check_val, 60)

#     ### --------------------- TrafficDateTime._check_next_time() ----------------------
#     def test_check_next_time_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_hr_min = "16:00"
#             check_val = test_obj._check_next_time()
#             self.assertIs(check_val, None)
        
#     def test_check_next_time_no_results(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = [(None,)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_hr_min = "20:00"
#             check_val = test_obj._check_next_time()
#             self.assertEqual(check_val, "tomorrow")

#     def test_check_next_time_return_result(self):
#         # define a mock result object
#         mock_result = mock.Mock()
#         mock_result.fetchall.return_value = [("16:15",)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_result)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.db.select") as mock_select:
#             test_obj = TrafficDateTime(mock_engine)
#             test_obj.curr_hr_min = "16:01"
#             check_val = test_obj._check_next_time()
#             self.assertIs(check_val, "16:15")

#     ### --------------------- TrafficDateTime.get_next_run_sleep_seconds() ----------------------
#     def test_get_next_run_sleep_seconds_not_traffic_day(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             with mock.patch("traffic_man.db_ops.TrafficDateTime._check_weekday", return_value=False) as mock_chk_weekday:
#                 with mock.patch("traffic_man.db_ops.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
#                     with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#                         mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

#                         test_obj = TrafficDateTime()
#                         check_val = test_obj.get_next_run_sleep_seconds()
#                         self.assertEqual(check_val, (120, True))

#     def test_get_next_run_sleep_seconds_is_holiday(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             with mock.patch("traffic_man.db_ops.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
#                 with mock.patch("traffic_man.db_ops.TrafficDateTime._check_holiday", return_value=True) as mock_chk_holiday:
#                     with mock.patch("traffic_man.db_ops.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
#                         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#                             mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

#                             test_obj = TrafficDateTime()
#                             check_val = test_obj.get_next_run_sleep_seconds()
#                             self.assertEqual(check_val, (120, True))

#     def test_get_next_run_sleep_seconds_next_time_tomorrow(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             with mock.patch("traffic_man.db_ops.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
#                 with mock.patch("traffic_man.db_ops.TrafficDateTime._check_holiday", return_value=False) as mock_chk_holiday:
#                     with mock.patch("traffic_man.db_ops.TrafficDateTime._check_next_time", return_value="tomorrow") as mock_chk_time:
#                         with mock.patch("traffic_man.db_ops.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
#                             with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#                                 mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

#                                 test_obj = TrafficDateTime()
#                                 check_val = test_obj.get_next_run_sleep_seconds()
#                                 self.assertEqual(check_val, (120, True))

#     def test_get_next_run_sleep_seconds_get_seconds(self):
#         with mock.patch("traffic_man.db_ops.TrafficDateTime.__init__", return_value=None) as mock_init:
#             with mock.patch("traffic_man.db_ops.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
#                 with mock.patch("traffic_man.db_ops.TrafficDateTime._check_holiday", return_value=False) as mock_chk_holiday:
#                     with mock.patch("traffic_man.db_ops.TrafficDateTime._check_next_time", return_value="16:15") as mock_chk_time:
#                         with mock.patch("traffic_man.db_ops.TrafficDateTime._get_seconds_to_time", return_value=90) as mock_chk_time:
#                             with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#                                 mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 16, 13, 30)

#                                 test_obj = TrafficDateTime()
#                                 check_val = test_obj.get_next_run_sleep_seconds()
#                                 self.assertEqual(check_val, (90, False))


# class TestTrafficData(unittest.TestCase):

#     ### --------------------- TrafficData.store_traffic_data() ----------------------
#     def test_store_traffic_data_except_on_execute(self):

#         test_traffic_json = {"datetime": "2022-05-01 16:15:27", "origin_addr": "100 N Main Street Fake City, Fake State 33333", "destination_addr": "100 N Main Street Fake City, Fake State 33333", "duration_sec": 1450, "duration_traffic_sec": 1387, "traffic_ratio": -0.056}
#         with mock.patch("traffic_man.db_ops.TrafficData.__init__", return_value=None) as mock_init:
#             # define a mock connection object
#             mock_conn = mock.Mock()
#             mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

#             # define a mock engine object
#             mock_engine = mock.Mock()         
#             mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#             mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#             test_obj = TrafficData()
#             test_obj.engine = mock_engine
#             check_val = test_obj.store_traffic_data(test_traffic_json)
#             self.assertIs(check_val, None)

#     def test_store_traffic_data_success(self):
#         test_traffic_json = {"datetime": "2022-05-01 16:15:27", "origin_addr": "100 N Main Street Fake City, Fake State 33333", "destination_addr": "100 N Main Street Fake City, Fake State 33333", "duration_sec": 1450, "duration_traffic_sec": 1387, "traffic_ratio": -0.056}
#         with mock.patch("traffic_man.db_ops.TrafficData.__init__", return_value=None) as mock_init:
#             # define a mock connection object
#             mock_conn = mock.Mock()
#             mock_conn.execute = mock.PropertyMock(return_value=None)

#             # define a mock engine object
#             mock_engine = mock.Mock()         
#             mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#             mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#             test_obj = TrafficData()
#             test_obj.engine = mock_engine
#             check_val = test_obj.store_traffic_data(test_traffic_json)
#             self.assertIs(check_val, True)
    
#     ### --------------------- TrafficData.check_traffic_conditions() ----------------------
#     def test_check_traffic_conditions_except_on_execution(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.check_traffic_conditions()
#                 self.assertIs(check_val, False)

#     def test_check_traffic_conditions_no_traffic_conditions(self):
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
#             with mock.patch("traffic_man.db_ops.traffic_conditions.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.check_traffic_conditions()
#                 self.assertIs(check_val, None)


#     def test_check_traffic_conditions_traffic_resolved(self):
#         # define a mock results object
#         mock_results = mock.Mock()
#         mock_results.fetchall.return_value = [(1, '2022-10-22', '2022-10-22 16:15:02', '2022-10-22 15:00:03')]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_results)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.check_traffic_conditions()
#                 self.assertEqual(check_val, "traffic_resolved")

#     def test_check_traffic_conditions_traffic(self):
#         # define a mock results object
#         mock_results = mock.Mock()
#         mock_results.fetchall.return_value = [(1, '2022-10-22', '2022-10-22 16:15:02', None)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_results)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.check_traffic_conditions()
#                 self.assertEqual(check_val, "traffic")

    
#     ### --------------------- TrafficData.write_bad_traffic() ----------------------
#     def test_write_bad_traffic_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.insert") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.write_bad_traffic()
#                 self.assertIs(check_val, None)

#     def test_write_bad_traffic_success(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock.Mock())

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.insert") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.write_bad_traffic()
#                 self.assertIs(check_val, True)

#     ### --------------------- TrafficData.write_traffic_resolved() ----------------------
#     def test_write_traffic_resolved_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.update") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.write_traffic_resolved()
#                 self.assertIs(check_val, None)

#     def test_write_traffic_resolved_success(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock.Mock())

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.traffic_conditions.update") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.write_traffic_resolved()
#                 self.assertIs(check_val, True)


#     ### --------------------- TrafficData.get_phone_numbers() ----------------------
#     def test_get_phone_numbers_except_on_execute(self):
#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.db.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.get_phone_numbers()
#                 self.assertIs(check_val, None)

#     def test_get_phone_numbers_two_phone_nums(self):
#         # define a mock results object
#         mock_results = mock.Mock()
#         mock_results.fetchall.return_value = [('+15555555555',),('+13333333333',)]

#         # define a mock connection object
#         mock_conn = mock.Mock()
#         mock_conn.execute = mock.PropertyMock(return_value=mock_results)

#         # define a mock engine object
#         mock_engine = mock.Mock()         
#         mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
#         mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

#         with mock.patch("traffic_man.db_ops.datetime") as mock_dt:
#             mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
#             with mock.patch("traffic_man.db_ops.db.select") as mock_select:
#                 test_obj = TrafficData(mock_engine)
#                 check_val = test_obj.get_phone_numbers()
#                 self.assertEqual(len(check_val), 2)
#                 self.assertEqual(check_val[1], '+13333333333')


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

