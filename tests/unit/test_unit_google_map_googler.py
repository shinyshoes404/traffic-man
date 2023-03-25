from unittest import TestCase, mock
import os, requests, urllib.parse
from traffic_man.google.map_googler import MapGoogler
from datetime import datetime




class TestMapGoogler(TestCase):
    
    ### ---------------- MapGoogler.__init__() ----------------    
    @mock.patch.dict(os.environ, {"GOOGLE_API_KEY":"fake-api-key"})
    def test_init_verify_vars(self):
        with mock.patch("traffic_man.google.map_googler.Config") as mock_config:
            mock_config.mode = "fake-mode"
            mock_config.language = "fake-lang"
            mock_config.traffic_model = "fake-model"  

            test_value = {'origins': 'place_id:fake-origin-place1|place_id:fake-origin-place2', 'destinations': 'place_id:fake-dest-place1|place_id:fake-dest-place2', 'traffic_model': 'fake-model', 'mode': 'fake-mode', 'language': 'fake-lang', 'departure_time': 'now', 'key': 'fake-api-key'}              
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            self.assertEqual(test_obj.params, test_value)
            self.assertEqual(test_obj.params_urlencode, urllib.parse.urlencode(test_obj.params, safe=":/"))
    
    ### ---------------- MapGoogler._call_google_maps() ---------------- 
    def test_call_google_maps_except_timeout(self):
        with mock.patch("traffic_man.google.map_googler.requests.get", side_effect=requests.exceptions.Timeout) as mock_get:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj._call_google_api()
            self.assertIs(check_val, None)

    def test_call_google_maps_except_sslerror(self):
        with mock.patch("traffic_man.google.map_googler.requests.get", side_effect=requests.exceptions.SSLError) as mock_get:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj._call_google_api()
            self.assertIs(check_val, None)
            
    def test_call_google_maps_except_unknown(self):
        with mock.patch("traffic_man.google.map_googler.requests.get", side_effect=Exception("unknown")) as mock_get:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj._call_google_api()
            self.assertIs(check_val, None)

    def test_call_google_maps_bad_status_code(self):
        with mock.patch("traffic_man.google.map_googler.requests.get") as mock_get:
            mock_get.return_value.status_code = 400
            mock_get.return_value.json.return_value = {"error":"bad request"}
            mock_get.return_value.content = b'{"error":"bad request"}'
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj._call_google_api()
            self.assertIs(check_val, None)

    def test_call_google_maps_success(self):
        with mock.patch("traffic_man.google.map_googler.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"mapsdata":"fake data"}
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj._call_google_api()
            self.assertEqual(check_val, {"mapsdata":"fake data"})

    ### ---------------- MapGoogler.google_with_retry() ---------------- 
    def test_google_with_retry_success_first_call(self):
        with mock.patch("traffic_man.google.map_googler.MapGoogler._call_google_api", return_value={"mapsdata":"fake data"}) as mock_call_google:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            check_val = test_obj.google_call_with_retry(2)
            self.assertEqual(check_val, {"mapsdata":"fake data"})
            self.assertEqual(mock_call_google.call_count, 1)

    @mock.patch("traffic_man.google.map_googler.sleep", return_value=None)
    def test_google_with_retry_success_second_call(self, mock_sleep):
        with mock.patch("traffic_man.google.map_googler.MapGoogler._call_google_api", side_effect=[None, {"mapsdata":"fake data"}]) as mock_call_google:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            check_val = test_obj.google_call_with_retry(2)
            self.assertEqual(check_val, {"mapsdata":"fake data"})
            self.assertEqual(mock_call_google.call_count, 2)


    @mock.patch("traffic_man.google.map_googler.sleep", return_value=None)
    def test_google_with_retry_success_too_many_calls(self, mock_sleep):
        with mock.patch("traffic_man.google.map_googler.MapGoogler._call_google_api", side_effect=[None, None]) as mock_call_google:
            test_obj = MapGoogler('place_id:fake-origin-place1|place_id:fake-origin-place2', 'place_id:fake-dest-place1|place_id:fake-dest-place2')
            check_val = test_obj.google_call_with_retry(2)
            self.assertIs(check_val, None)
            self.assertEqual(mock_call_google.call_count, 2)

    ### ---------------- MapGoogler.build_orig_dest_lists() ----------------
    def test_build_orig_dest_lists_build_lists(self):
        test_orig_dest_set = [["orig1", "orig2"], 3, [["dest1"], ["dest2", "dest3"]]]
        expected_orig_list = "place_id:orig1|place_id:orig2"
        expected_dest_list = "place_id:dest1|place_id:dest2|place_id:dest3"
        check_val = MapGoogler.build_orig_dest_lists(test_orig_dest_set)
        self.assertEqual(check_val, (expected_orig_list, expected_dest_list))

    ### ---------------- MapGoogler.calc_traffic() ---------------- 
    def test_calc_traffic_get_structured_data(self):
        test_json = {"json":"will not work"}
        test_orig_dest_set = [["orig1", "orig2"], 3, [["dest1"], ["dest2", "dest3"]]]
        with mock.patch("traffic_man.google.map_googler.MapGoogler._get_dest_counts", return_value=[1,2]) as mock_get_dest_counts:
            with mock.patch("traffic_man.google.map_googler.MapGoogler._extract_data", return_value=[{"fake": "structured data"}]) as mock_extract_data:
                check_val = MapGoogler.calc_traffic(test_json, test_orig_dest_set)
                self.assertEqual(check_val, [{"fake": "structured data"}])

    def test_calc_traffic_extract_data_none(self):
        test_json = {"json":"will not work"}
        test_orig_dest_set = [["orig1", "orig2"], 3, [["dest1"], ["dest2", "dest3"]]]
        with mock.patch("traffic_man.google.map_googler.MapGoogler._get_dest_counts", return_value=[1,2]) as mock_get_dest_counts:
            with mock.patch("traffic_man.google.map_googler.MapGoogler._extract_data", return_value=None) as mock_extract_data:
                check_val = MapGoogler.calc_traffic(test_json, test_orig_dest_set)
                self.assertIs(check_val, None)

    ### ---------------- MapGoogler._get_dest_counts() ---------------- 
    def test_get_dest_counts(self):
        test_orig_dest_set = [["orig1", "orig2"], 3, [["dest1"], ["dest2", "dest3"]]]
        check_val = MapGoogler._get_dest_counts(test_orig_dest_set)
        self.assertEqual(check_val, [1,2])

    ### ---------------- MapGoogler._extract_data() ----------------      
    # ----- test data to reuse -----  
    test_orig_dest_set = [["fake-orig1", "fake-orig2"], 3, [["fake-dest1", "fake-dest2"], ["fake-dest3"]]]
    test_dest_counts = [2, 1]

    def test_extract_data_rows_none(self):
        check_val = MapGoogler._extract_data(TestMapGoogler.test_dest_counts, {"bad": "data"}, TestMapGoogler.test_orig_dest_set)
        self.assertIs(check_val, None)
 
    def test_extract_data_no_row_data(self):
        check_val = MapGoogler._extract_data(
            TestMapGoogler.test_dest_counts,
            {"origin_addresses":["fake-orig-addr1", "fake-orig-addr2"], 
            "destination_addresses": ["fake-dest-addr1", "fake-dest-addr2", "fake-dest-addr3"],
            "rows":[]},
            TestMapGoogler.test_orig_dest_set
            )
        self.assertIs(check_val, None)    

    def test_extract_data_exception(self):
        check_val = MapGoogler._extract_data(
            TestMapGoogler.test_dest_counts,
            {"origin_addresses":["fake-orig-addr1", "fake-orig-addr2"], 
            "destination_addresses": ["fake-dest-addr1", "fake-dest-addr2", "fake-dest-addr3"],
            "rows":
                [
                    {"elements":[
                        # divide by zero will create an exception
                        {"duration":{"value":0},"duration_in_traffic":{"value":10}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":11}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":12}}
                     ]
                    },
                    {"elements":[
                        {"duration":{"value":10},"duration_in_traffic":{"value":13}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":14}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":15}}
                     ]
                    }
                ]},
            TestMapGoogler.test_orig_dest_set
            )
        self.assertIs(check_val, None)

    @mock.patch("traffic_man.google.map_googler.datetime")
    def test_extract_data_success(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2022, 1, 1, 0, 0, 0)
        check_val = MapGoogler._extract_data(
            TestMapGoogler.test_dest_counts,
            {"origin_addresses":["fake-orig-addr1", "fake-orig-addr2"], 
            "destination_addresses": ["fake-dest-addr1", "fake-dest-addr2", "fake-dest-addr3"],
            "rows":
                [
                    {"elements":[
                        {"duration":{"value":10},"duration_in_traffic":{"value":10}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":11}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":12}}
                     ]
                    },
                    {"elements":[
                        {"duration":{"value":10},"duration_in_traffic":{"value":13}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":14}},
                        {"duration":{"value":10},"duration_in_traffic":{"value":15}}
                     ]
                    }
                ]},
            TestMapGoogler.test_orig_dest_set
            )
        expected_data = [
            {"datetime": "2022-01-01 00:00:00", "origin_addr": "fake-orig-addr1", "destination_addr": "fake-dest-addr1", "duration_sec": 10, "duration_traffic_sec": 10, "traffic_ratio": 0, "orig_place_id": "fake-orig1", "dest_place_id": "fake-dest1" },
            {"datetime": "2022-01-01 00:00:00", "origin_addr": "fake-orig-addr1", "destination_addr": "fake-dest-addr2", "duration_sec": 10, "duration_traffic_sec": 11, "traffic_ratio": 0.1, "orig_place_id": "fake-orig1", "dest_place_id": "fake-dest2" },
            {"datetime": "2022-01-01 00:00:00", "origin_addr": "fake-orig-addr2", "destination_addr": "fake-dest-addr3", "duration_sec": 10, "duration_traffic_sec": 15, "traffic_ratio": 0.5, "orig_place_id": "fake-orig2", "dest_place_id": "fake-dest3" }
        ]

        self.assertEqual(check_val, expected_data)
