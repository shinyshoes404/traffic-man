import unittest, mock, datetime
from traffic_man.db.traffic_data import TrafficData

class TestTrafficData(unittest.TestCase):

    ### --------------------- TrafficData.store_traffic_data() ----------------------
    def test_store_traffic_data_except_on_execute(self):

        test_traffic_json = {"datetime": "2022-05-01 16:15:27", 
                            "orig_place_id": "fakeorigplaceid",
                            "origin_addr": "100 N Main Street Fake City, Fake State 33333",
                            "dest_place_id": "fakedestplaceid",
                            "destination_addr": "100 N Main Street Fake City, Fake State 33333",
                            "duration_sec": 1450, "duration_traffic_sec": 1387, "traffic_ratio": -0.056}

        with mock.patch("traffic_man.db.traffic_data.TrafficData.__init__", return_value=None) as mock_init:
            # define a mock connection object
            mock_conn = mock.Mock()
            mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

            # define a mock engine object
            mock_engine = mock.Mock()         
            mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
            mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

            test_obj = TrafficData()
            test_obj.engine = mock_engine
            check_val = test_obj.store_traffic_data(test_traffic_json)
            self.assertIs(check_val, None)

    def test_store_traffic_data_success(self):
        test_traffic_json = {"datetime": "2022-05-01 16:15:27", 
                            "orig_place_id": "fakeorigplaceid",
                            "origin_addr": "100 N Main Street Fake City, Fake State 33333",
                            "dest_place_id": "fakedestplaceid",
                            "destination_addr": "100 N Main Street Fake City, Fake State 33333",
                            "duration_sec": 1450, "duration_traffic_sec": 1387, "traffic_ratio": -0.056}
        
        with mock.patch("traffic_man.db.traffic_data.TrafficData.__init__", return_value=None) as mock_init:
            # define a mock connection object
            mock_conn = mock.Mock()
            mock_conn.execute = mock.PropertyMock(return_value=None)

            # define a mock engine object
            mock_engine = mock.Mock()         
            mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
            mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

            test_obj = TrafficData()
            test_obj.engine = mock_engine
            check_val = test_obj.store_traffic_data(test_traffic_json)
            self.assertIs(check_val, True)
    
    ### --------------------- TrafficData.check_traffic_conditions() ----------------------
    def test_check_traffic_conditions_except_on_execution(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.select") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.check_traffic_conditions()
                self.assertIs(check_val, False)

    def test_check_traffic_conditions_no_traffic_conditions(self):
        # define a mock results object
        mock_results = mock.Mock()
        mock_results.fetchall.return_value = []

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_results)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.select") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.check_traffic_conditions()
                self.assertEqual(check_val, {})


    def test_check_traffic_conditions_traffic_resolved(self):
        # define a mock results object
        mock_results = mock.Mock()
        mock_results.fetchall.return_value = [(1,
                                             '2022-10-22', 
                                             'DhIJr7A7RcQEyYcRfYNPekurSZQ',
                                             'JrIJr7A7RcQEyYcRfYNPekurSZB',
                                             '2022-10-22 16:15:02',
                                             '2022-10-22 15:00:03')]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_results)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.select") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.check_traffic_conditions()
                self.assertEqual(check_val, {'DhIJr7A7RcQEyYcRfYNPekurSZQ|JrIJr7A7RcQEyYcRfYNPekurSZB': 'traffic_resolved'})

    def test_check_traffic_conditions_traffic(self):
        # define a mock results object
        mock_results = mock.Mock()
        mock_results.fetchall.return_value = [(1,
                                             '2022-10-22', 
                                             'DhIJr7A7RcQEyYcRfYNPekurSZQ',
                                             'JrIJr7A7RcQEyYcRfYNPekurSZB',
                                             '2022-10-22 16:15:02',
                                             None)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_results)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.select") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.check_traffic_conditions()
                self.assertEqual(check_val, {'DhIJr7A7RcQEyYcRfYNPekurSZQ|JrIJr7A7RcQEyYcRfYNPekurSZB': 'traffic'})

    
    ### --------------------- TrafficData.write_bad_traffic() ----------------------
    def test_write_bad_traffic_except_on_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.insert") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.write_bad_traffic("fakeorigid", "fakedestid")
                self.assertIs(check_val, None)

    def test_write_bad_traffic_success(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock.Mock())

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.insert") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.write_bad_traffic("fakeorigid", "fakedestid")
                self.assertIs(check_val, True)

    ### --------------------- TrafficData.write_traffic_resolved() ----------------------
    def test_write_traffic_resolved_except_on_execute(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("execute exception"))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.update") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.write_traffic_resolved("fakeorigid", "fakedestid")
                self.assertIs(check_val, None)

    def test_write_traffic_resolved_success(self):
        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock.Mock())

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.traffic_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.traffic_data.traffic_conditions.update") as mock_select:
                test_obj = TrafficData(mock_engine)
                check_val = test_obj.write_traffic_resolved("fakeorigid", "fakedestid")
                self.assertIs(check_val, True)