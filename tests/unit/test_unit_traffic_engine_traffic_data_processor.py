from unittest import TestCase, mock
import pandas as pd
from traffic_man.traffic_engine.traffic_data_processor import TrafficDataProc


#### ------- DEFINING DATA TO USE WITH TESTS ------- ###
class TestStructGoogleData:
    correct_data = [
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig1 addr string",
            "destination_addr": "dest1 addr string",
            "duration_sec": 1231,
            "duration_traffic_sec": 1241,
            "traffic_ratio": 0.011,
            "orig_place_id": "orig1id",
            "dest_place_id": "dest1id"
            },
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig2 addr string",
            "destination_addr": "dest2 addr string",
            "duration_sec": 1232,
            "duration_traffic_sec": 1242,
            "traffic_ratio": 0.012,
            "orig_place_id": "orig2id",
            "dest_place_id": "dest2id"
            },
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig3 addr string",
            "destination_addr": "dest3 addr string",
            "duration_sec": 1233,
            "duration_traffic_sec": 1243,
            "traffic_ratio": 0.013,
            "orig_place_id": "orig3id",
            "dest_place_id": "dest3id"
            }
        ]

    missing_orig_place_id = [
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig1 addr string",
            "destination_addr": "dest1 addr string",
            "duration_sec": 1231,
            "duration_traffic_sec": 1241,
            "traffic_ratio": 0.011,
            "not_orig_place_id": "orig1id",
            "dest_place_id": "dest1id"
            },
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig2 addr string",
            "destination_addr": "dest2 addr string",
            "duration_sec": 1232,
            "duration_traffic_sec": 1242,
            "traffic_ratio": 0.012,
            "not_orig_place_id": "orig2id",
            "dest_place_id": "dest2id"
            },
            {
            "datetime": "2022-12-27 14:12:43",
            "origin_addr": "orig3 addr string",
            "destination_addr": "dest3 addr string",
            "duration_sec": 1233,
            "duration_traffic_sec": 1243,
            "traffic_ratio": 0.013,
            "not_orig_place_id": "orig3id",
            "dest_place_id": "dest3id"
            }
        ]

    fail_to_build_df = "random string"
    

class TestTrafficCondData:

    correct_data = {"orig1id|dest1id": "traffic", "orig2id|dest2id": "traffic_resolved"}
    fail_to_build_df = "random string"
    empty_traffic_cond = {}
          
class TestGoogleDataDF:
    correct_df = pd.DataFrame(TestStructGoogleData.correct_data)
    correct_df["orig_dest_combined"] = correct_df["orig_place_id"] + "|" + correct_df["dest_place_id"]

class TestTrafficCondDF:
    correct_df = pd.DataFrame(TestTrafficCondData.correct_data.items(), columns = ["orig_dest_placeids", "traffic_condition"])
    wrong_col_name_df = correct_df.rename(columns={"traffic_condition": "not_traffic_conditiion"})



#### ---------------------------- TESTS ---------------------------- ####

class TestTrafficDataProc(TestCase):

    ### --------------------- TrafficDataProc.build_dfs() ----------------------
    def test_build_dfs_fail_google_traffic_df(self):
        test_obj = TrafficDataProc(TestStructGoogleData.fail_to_build_df, TestTrafficCondData.correct_data)
        self.assertIs(test_obj.build_dfs(), None)
    
    def test_build_dfs_fail_orig_dest_df(self):
        test_obj = TrafficDataProc(TestStructGoogleData.missing_orig_place_id, TestTrafficCondData.correct_data)
        self.assertIs(test_obj.build_dfs(), None)
    
    def test_build_dfs_fail_traffic_cond_df(self):
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.fail_to_build_df)
        self.assertIs(test_obj.build_dfs(), None)
    
    def test_build_dfs_success_empty_traffic_cond(self):
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.empty_traffic_cond)
        self.assertIs(test_obj.build_dfs(), True)
    
    def test_build_dfs_success_with_traffic_cond_data(self):
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        self.assertIs(test_obj.build_dfs(), True)
    
    ### --------------------- TrafficDataProc.get_new_bad_traffic() ----------------------
    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_new_bad_traffic_except_on_merge(self, mock_config):
        mock_config.overage_parameter = 0.01
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = None

        self.assertIs(test_obj.get_new_bad_traffic(), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_new_bad_traffic_except_on_merged_query(self, mock_config):
        mock_config.overage_parameter = 0.010
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.wrong_col_name_df

        self.assertIs(test_obj.get_new_bad_traffic(), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_new_bad_traffic_return_result(self, mock_config):
        mock_config.overage_parameter = 0.010
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.correct_df

        expected_data = [
                        {
                        'datetime': '2022-12-27 14:12:43',
                        'origin_addr': 'orig3 addr string',
                        'destination_addr': 'dest3 addr string',
                        'duration_sec': 1233,
                        'duration_traffic_sec': 1243,
                        'traffic_ratio': 0.013,
                        'orig_place_id': 'orig3id',
                        'dest_place_id': 'dest3id',
                        'orig_dest_combined':'orig3id|dest3id',
                        'orig_dest_placeids': None,
                        'traffic_condition': None
                        }
                        ]

        self.assertEqual(test_obj.get_new_bad_traffic(), expected_data)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_new_bad_traffic_return_empty_list(self, mock_config):
        mock_config.overage_parameter = 1.0
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.correct_df

        self.assertEqual(test_obj.get_new_bad_traffic(), [])

    # ### --------------------- TrafficDataProc.get_resolved_traffic() ----------------------
    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_resolved_traffic_except_on_merge(self, mock_config):
        mock_config.overage_parameter = 0.014 * 2
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = None

        self.assertIs(test_obj.get_resolved_traffic(), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_resolved_traffic_except_on_merged_query(self, mock_config):
        mock_config.overage_parameter = 0.014 * 2
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.wrong_col_name_df

        self.assertIs(test_obj.get_resolved_traffic(), None)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_resolved_traffic_return_result(self, mock_config):
        mock_config.overage_parameter = 0.014 * 2
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.correct_df

        expected_data = [
                    {
                    'datetime': '2022-12-27 14:12:43',
                    'origin_addr': 'orig1 addr string',
                    'destination_addr': 'dest1 addr string',
                    'duration_sec': 1231,
                    'duration_traffic_sec': 1241,
                    'traffic_ratio': 0.011,
                    'orig_place_id': 'orig1id',
                    'dest_place_id': 'dest1id',
                    'orig_dest_combined': 'orig1id|dest1id',
                    'orig_dest_placeids': 'orig1id|dest1id',
                    'traffic_condition': 'traffic'
                    }
                ]

        self.assertEqual(test_obj.get_resolved_traffic(), expected_data)

    @mock.patch("traffic_man.traffic_engine.traffic_data_processor.Config")
    def test_get_resolved_traffic_return_empty_list(self, mock_config):
        mock_config.overage_parameter = 0.001
        test_obj = TrafficDataProc(TestStructGoogleData.correct_data, TestTrafficCondData.correct_data)
        test_obj.google_data_df = TestGoogleDataDF.correct_df
        test_obj.traffic_conditions_df = TestTrafficCondDF.correct_df

        self.assertEqual(test_obj.get_resolved_traffic(), [])