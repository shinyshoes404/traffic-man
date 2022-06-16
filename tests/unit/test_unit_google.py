import mock, unittest, os, requests
import urllib.parse
from traffic_man.google import MapGoogler




class TestMapGoogler(unittest.TestCase):
    
    ### ---------------- MapGoogler.__init__() ----------------    
    @mock.patch.dict(os.environ, {"ORIGIN_PLACE_ID":"fake-origin-place", "DEST_PLACE_ID":"fake-dest-place", "GOOGLE_API_KEY":"fake-api-key"})
    def test_init_verify_vars(self):
        with mock.patch("traffic_man.google.Config") as mock_config:
            mock_config.mode = "fake-mode"
            mock_config.language = "fake-lang"
            mock_config.traffic_model = "fake-model"  

            test_value = {'origins': 'place_id:fake-origin-place', 'destinations': 'place_id:fake-dest-place', 'traffic_model': 'fake-model', 'mode': 'fake-mode', 'language': 'fake-lang', 'departure_time': 'now', 'key': 'fake-api-key'}              
            test_obj = MapGoogler()
            self.assertEqual(test_obj.params, test_value)
            self.assertEqual(test_obj.params_urlencode, urllib.parse.urlencode(test_obj.params, safe=":/"))
    
    ### ---------------- MapGoogler.call_google_maps() ---------------- 
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_call_google_maps_except_timeout(self, mock_init):
        with mock.patch("traffic_man.google.requests.get", side_effect=requests.exceptions.Timeout) as mock_get:
            test_obj = MapGoogler()
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj.call_google_maps()
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_call_google_maps_except_sslerror(self, mock_init):
        with mock.patch("traffic_man.google.requests.get", side_effect=requests.exceptions.SSLError) as mock_get:
            test_obj = MapGoogler()
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj.call_google_maps()
            self.assertIs(check_val, None)
            
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_call_google_maps_except_unknown(self, mock_init):
        with mock.patch("traffic_man.google.requests.get", side_effect=Exception("unknown")) as mock_get:
            test_obj = MapGoogler()
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj.call_google_maps()
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_call_google_maps_bad_status_code(self, mock_init):
        with mock.patch("traffic_man.google.requests.get") as mock_get:
            mock_get.return_value.status_code = 400
            mock_get.return_value.json.return_value = {"error":"bad request"}
            mock_get.return_value.content = b'{"error":"bad request"}'
            test_obj = MapGoogler()
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj.call_google_maps()
            self.assertIs(check_val, None)

    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_call_google_maps_success(self, mock_init):
        with mock.patch("traffic_man.google.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"mapsdata":"fake data"}
            test_obj = MapGoogler()
            test_obj.base_url = "fake-url"
            test_obj.params_urlencode = "fake-urlencoded"

            check_val = test_obj.call_google_maps()
            self.assertEqual(check_val, {"mapsdata":"fake data"})

    ### ---------------- MapGoogler.google_with_retry() ---------------- 
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_google_with_retry_success_first_call(self, mock_init):
        with mock.patch("traffic_man.google.MapGoogler.call_google_maps", return_value={"mapsdata":"fake data"}) as mock_call_google:
            test_obj = MapGoogler()
            check_val = test_obj.google_call_with_retry(2)
            self.assertEqual(check_val, {"mapsdata":"fake data"})

    @mock.patch("traffic_man.google.sleep", return_value=None)
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_google_with_retry_success_second_call(self, mock_init, mock_sleep):
        with mock.patch("traffic_man.google.MapGoogler.call_google_maps", side_effect=[None, {"mapsdata":"fake data"}]) as mock_call_google:
            test_obj = MapGoogler()
            check_val = test_obj.google_call_with_retry(2)
            self.assertEqual(check_val, {"mapsdata":"fake data"})
            self.assertEqual(mock_call_google.call_count, 2)

    @mock.patch("traffic_man.google.sleep", return_value=None)
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_google_with_retry_success_too_man_calls(self, mock_init, mock_sleep):
        with mock.patch("traffic_man.google.MapGoogler.call_google_maps", side_effect=[None, None]) as mock_call_google:
            test_obj = MapGoogler()
            check_val = test_obj.google_call_with_retry(2)
            self.assertIs(check_val, None)
            self.assertEqual(mock_call_google.call_count, 2)

    ### ---------------- MapGoogler.calc_traffic() ---------------- 
    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_calc_traffic_except(self, mock_init):
        test_json = {"json":"will not work"}
        check_val = MapGoogler.calc_traffic(test_json)
        self.assertIs(check_val, None)

    @mock.patch("traffic_man.google.MapGoogler.__init__", return_value=None)
    def test_calc_traffic_works(self, mock_init):
        test_json = {
            "origin_addresses":["fake-origin"], 
            "destination_addresses": ["fake-destination"],
            "rows":
                [
                    {"elements":[
                        {
                            "duration":{
                                "value":10
                            },
                            "duration_in_traffic":{
                                "value":15
                            }
                        }
                     ]
                    }
                ]
            }

        check_val = MapGoogler.calc_traffic(test_json)
        self.assertEqual(check_val["traffic_ratio"], .5)