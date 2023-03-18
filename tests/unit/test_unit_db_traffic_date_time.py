from unittest import TestCase, mock
import datetime
from traffic_man.db.traffic_date_time import TrafficDateTime


class TestTrafficDateTime(TestCase):

    ### --------------------- TrafficDateTime._get_1201_tomorrow() ----------------------
    @mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None)
    def test_get_1201_tomorrow(self, mock_init):
        test_obj = TrafficDateTime()
        test_obj.curr_date = "2022-10-22"
        self.assertEqual(test_obj._get_1201_tomorrow(), datetime.datetime(2022, 10, 23, 0, 1))

    ### --------------------- TrafficDateTime._check_weekday() ----------------------
    def test_check_weekday_except_on_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.check_days.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_weekday = "wednesday"
            check_val = test_obj._check_weekday()
            self.assertIs(check_val, None)
        
    def test_check_weekday_not_a_traffic_check_day(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = []

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.check_days.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_weekday = "sunday"
            check_val = test_obj._check_weekday()
            self.assertIs(check_val, False)

    def test_check_weekday_traffic_check_day(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = [("monday",)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.check_days.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_weekday = "monday"
            check_val = test_obj._check_weekday()
            self.assertIs(check_val, True)


    ### --------------------- TrafficDateTime._check_holiday() ----------------------
    def test_check_holiday_except_on_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.holidays.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_date = "2022-07-05"
            check_val = test_obj._check_holiday()
            self.assertIs(check_val, None)
        
    def test_check_holiday_not_a_holiday(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = []

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.holidays.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_date = "2022-07-05"
            check_val = test_obj._check_holiday()
            self.assertIs(check_val, False)

    def test_check_holiday_is_holiday(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = [("2022-07-04",)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.holidays.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_date = "2022-07-04"
            check_val = test_obj._check_holiday()
            self.assertIs(check_val, True)

    ### --------------------- TrafficDateTime._get_seconds_to_time() ----------------------
    def test_get_seconds_to_time(self):
        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None) as mock_init:
            test_obj = TrafficDateTime()
            test_obj.curr_date = "2022-10-22"
            test_obj.curr_datetime = datetime.datetime(2022, 10, 22, 0, 0, 0)
            check_val = test_obj._get_seconds_to_time("00:01")
            self.assertEqual(check_val, 60)

    ### --------------------- TrafficDateTime._check_next_time() ----------------------
    def test_check_next_time_except_on_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("select exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.db.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_hr_min = "16:00"
            check_val = test_obj._check_next_time()
            self.assertIs(check_val, None)
        
    def test_check_next_time_no_results(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = [(None,)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.db.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_hr_min = "20:00"
            check_val = test_obj._check_next_time()
            self.assertEqual(check_val, "tomorrow")

    def test_check_next_time_return_result(self):
        # define a mock result object
        mock_result = mock.Mock()
        mock_result.fetchall.return_value = [("16:15",)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_result)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_date_time.db.select") as mock_select:
            test_obj = TrafficDateTime(mock_engine)
            test_obj.curr_hr_min = "16:01"
            check_val = test_obj._check_next_time()
            self.assertIs(check_val, "16:15")

    ### --------------------- TrafficDateTime.get_next_run_sleep_seconds() ----------------------
    def test_get_next_run_sleep_seconds_not_traffic_day(self):
        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None) as mock_init:
            with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_weekday", return_value=False) as mock_chk_weekday:
                with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
                    with mock.patch("traffic_man.db.traffic_date_time.datetime") as mock_dt:
                        mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

                        test_obj = TrafficDateTime()
                        check_val = test_obj.get_next_run_sleep_seconds()
                        self.assertEqual(check_val, (120, True))

    def test_get_next_run_sleep_seconds_is_holiday(self):
        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None) as mock_init:
            with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
                with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_holiday", return_value=True) as mock_chk_holiday:
                    with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
                        with mock.patch("traffic_man.db.traffic_date_time.datetime") as mock_dt:
                            mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

                            test_obj = TrafficDateTime()
                            check_val = test_obj.get_next_run_sleep_seconds()
                            self.assertEqual(check_val, (120, True))

    def test_get_next_run_sleep_seconds_next_time_tomorrow(self):
        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None) as mock_init:
            with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
                with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_holiday", return_value=False) as mock_chk_holiday:
                    with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_next_time", return_value="tomorrow") as mock_chk_time:
                        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._get_1201_tomorrow", return_value=datetime.datetime(2022, 10, 22, 0, 1, 0)) as mock_tomorrow:
                            with mock.patch("traffic_man.db.traffic_date_time.datetime") as mock_dt:
                                mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 23, 59, 0)

                                test_obj = TrafficDateTime()
                                check_val = test_obj.get_next_run_sleep_seconds()
                                self.assertEqual(check_val, (120, True))

    def test_get_next_run_sleep_seconds_get_seconds(self):
        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime.__init__", return_value=None) as mock_init:
            with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_weekday", return_value=True) as mock_chk_weekday:
                with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_holiday", return_value=False) as mock_chk_holiday:
                    with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._check_next_time", return_value="16:15") as mock_chk_time:
                        with mock.patch("traffic_man.db.traffic_date_time.TrafficDateTime._get_seconds_to_time", return_value=90) as mock_chk_time:
                            with mock.patch("traffic_man.db.traffic_date_time.datetime") as mock_dt:
                                mock_dt.now.return_value = datetime.datetime(2022, 10, 21, 16, 13, 30)

                                test_obj = TrafficDateTime()
                                check_val = test_obj.get_next_run_sleep_seconds()
                                self.assertEqual(check_val, (90, False))


