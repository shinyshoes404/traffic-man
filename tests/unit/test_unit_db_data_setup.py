from unittest import TestCase, mock
from traffic_man.db.data_setup import DataSetup

class TestDataSetup(TestCase):

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