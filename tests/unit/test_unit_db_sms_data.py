import unittest, mock, datetime
from traffic_man.db.sms_data import SMSData

@mock.patch("traffic_man.db.sms_data.datetime")
@mock.patch("traffic_man.db.sms_data.sms_data.select")
@mock.patch("traffic_man.db.sms_data.phone_numbers.select")
@mock.patch("traffic_man.db.sms_data.select")
@mock.patch("traffic_man.db.sms_data.outerjoin")
class TestSMSDataGetPhoneNums(unittest.TestCase):

    ### --------------------- SMSData.get_phone_nums() ----------------------
    def test_get_phone_nums_except_on_execute(self, mock_outerjoin, mock_select, mock_phone_num_select, mock_sms_data_select, mock_dt):

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception('execute exception'))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
        test_obj = SMSData(mock_engine)
        check_val = test_obj.get_phone_nums("fakesmstype", "fakeorigid", "fakedestid")
        self.assertIs(check_val, None)

    def test_get_phone_nums_no_results(self, mock_outerjoin, mock_select, mock_phone_num_select, mock_sms_data_select, mock_dt):
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

        with mock.patch("traffic_man.db.sms_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.sms_data.sms_data.select") as mock_smselect:
                test_obj = SMSData(mock_engine)
                check_val = test_obj.get_phone_nums("fakesmstype", "fakeorigid", "fakedestid")
                self.assertEqual(check_val, [])

    def test_get_phone_nums_results_returned(self, mock_outerjoin, mock_select, mock_phone_num_select, mock_sms_data_select, mock_dt):
        # define a mock results object
        mock_results = mock.Mock()
        mock_results.fetchall.return_value = [("+12222222222",), ("+13333333333",)]

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=mock_results)

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        with mock.patch("traffic_man.db.sms_data.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
            with mock.patch("traffic_man.db.sms_data.sms_data.select") as mock_smselect:
                test_obj = SMSData(mock_engine)
                check_val = test_obj.get_phone_nums("fakesmstype", "fakeorigid", "fakedestid")
                self.assertEqual(check_val, ["+12222222222", "+13333333333"])


@mock.patch("traffic_man.db.sms_data.datetime")
@mock.patch("traffic_man.db.sms_data.sms_data.insert")
class TestSMSDataWriteSMSRecords(unittest.TestCase):
    sms_data_list = [
            {"sms_type": "bad traffic", "status": "sent", "direction": "outbound", "msg_content": "Traffic is looking pretty bad", "phone_num": "+12222222222"},
            {"sms_type": "bad traffic", "status": "sent", "direction": "outbound", "msg_content": "Traffic is looking pretty bad", "phone_num": "+13333333333"},
        ]

    ### --------------------- SMSData.write_sms_records() ----------------------
    def test_write_sms_records_except_on_execute(self, mock_sms_data_insert, mock_dt):

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception('execute exception'))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
        test_obj = SMSData(mock_engine)
        check_val = test_obj.write_sms_records(self.sms_data_list)
        self.assertEqual(check_val, 2)

    def test_write_sms_records_sucessful_write(self, mock_sms_data_insert, mock_dt):

        # define a mock connection object
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(return_value=(1,))

        # define a mock engine object
        mock_engine = mock.Mock()         
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_engine.connect.return_value.__enter__.return_value = mock_conn # need .return_value.__enter__.return_value for the with as statement in our app

        mock_dt.now.return_value = datetime.datetime(2022, 10, 22, 0, 0) # sets self.curr_date in __init__
        test_obj = SMSData(mock_engine)
        check_val = test_obj.write_sms_records(self.sms_data_list)
        self.assertEqual(check_val, 0)