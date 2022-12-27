from unittest import TestCase, mock

from traffic_man.db.users import UserData

@mock.patch("traffic_man.db.users.db.select")
@mock.patch("traffic_man.db.users.phone_numbers")
class TestUserData(TestCase):


    ### --------------------- UserData.get_orig_dest_pairs() ----------------------
    def test_get_orig_dest_pairs_except_on_execute(self, mock_phone_nums, mock_db):
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("execution exception"))
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertIs(test_obj.get_orig_dest_pairs(), False)

    def test_get_orig_dest_pairs_zero_rows(self, mock_phone_nums, mock_db):
        mock_results_obj = mock.Mock()
        mock_results_obj.fetchall.return_value = []
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn.execute.return_value = mock_results_obj
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertIs(test_obj.get_orig_dest_pairs(), None)

    def test_get_orig_dest_pairs_results_returned(self, mock_phone_nums, mock_db):
        result_data = [("orig1", "dest1"), ("orig2", "dest2"), ("orig3", "dest3")]
        expected_return = [["orig1","dest1"],["orig2","dest2"],["orig3", "dest3"]]
        
        mock_results_obj = mock.Mock()
        mock_results_obj.fetchall.return_value = result_data
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn.execute.return_value = mock_results_obj
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertEqual(test_obj.get_orig_dest_pairs(), expected_return)

    
    ### --------------------- UserData.get_sub_phone_numbers_by_orig_dest_pair() ----------------------
    def test_get_sub_phone_numbers_by_orig_dest_pair_exception_on_execute(self, mock_phone_nums, mock_db):
        input_orig_dest_pair = ["orig1", "dest1"]
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(side_effect=Exception("execution exception"))
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertIs(test_obj.get_sub_phone_numbers_by_orig_dest_pair(input_orig_dest_pair), False)

    def test_get_sub_phone_numbers_by_orig_dest_pair_zero_rows(self, mock_phone_nums, mock_db):
        input_orig_dest_pair = ["orig1", "dest1"]
        mock_results_obj = mock.Mock()
        mock_results_obj.fetchall.return_value = []
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn.execute.return_value = mock_results_obj
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertIs(test_obj.get_sub_phone_numbers_by_orig_dest_pair(input_orig_dest_pair), None)

    def test_get_sub_phone_numbers_by_orig_dest_pair_results_returned(self, mock_phone_nums, mock_db):
        input_orig_dest_pair = ["orig1", "dest1"]
        results_data = [("+12222222222",), ("+13333333333",), ("+14444444444",)]

        mock_results_obj = mock.Mock()
        mock_results_obj.fetchall.return_value = results_data
        mock_engine = mock.Mock()
        mock_engine.connect = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn = mock.Mock()
        mock_conn.execute = mock.PropertyMock(new_callable=mock.Mock())
        mock_conn.execute.return_value = mock_results_obj
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        test_obj = UserData(mock_engine)
        self.assertIs(test_obj.get_sub_phone_numbers_by_orig_dest_pair(input_orig_dest_pair), results_data)
