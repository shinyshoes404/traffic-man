import unittest, mock

from traffic_man.entrypoint import main

@mock.patch("traffic_man.entrypoint.db")
@mock.patch("traffic_man.entrypoint.metadata_obj")
class Testentrypoint_datasetup(unittest.TestCase):

    ### ------------------------- entrypoint.main() -----------------------------
    def test_main_data_setup_fail_update_check_times(self, mock_meta_obj, mock_db):
        with mock.patch("traffic_man.entrypoint.DataSetup") as mock_datasetup:
            mock_datasetup.return_value.update_check_times.return_value = None

            check_val = main()
            self.assertIs(check_val, None)

    def test_main_data_setup_fail_update_holidays(self, mock_meta_obj, mock_db):
        with mock.patch("traffic_man.entrypoint.DataSetup") as mock_datasetup:
            mock_datasetup.return_value.update_check_times.return_value = True
            mock_datasetup.return_value.update_holidays.return_value = None

            check_val = main()
            self.assertIs(check_val, None)

    def test_main_data_setup_fail_update_check_days(self, mock_meta_obj, mock_db):
        with mock.patch("traffic_man.entrypoint.DataSetup") as mock_datasetup:
            mock_datasetup.return_value.update_check_times.return_value = True
            mock_datasetup.return_value.update_holidays.return_value = True
            mock_datasetup.return_value.update_check_days.return_value = None

            check_val = main()
            self.assertIs(check_val, None)

    def test_main_data_setup_fail_update_phone_numbers(self, mock_meta_obj, mock_db):
        with mock.patch("traffic_man.entrypoint.DataSetup") as mock_datasetup:
            mock_datasetup.return_value.update_check_times.return_value = True
            mock_datasetup.return_value.update_holidays.return_value = True
            mock_datasetup.return_value.update_check_days.return_value = True
            mock_datasetup.return_value.update_phone_numbers.return_value = None

            check_val = main()
            self.assertIs(check_val, None)


@mock.patch("traffic_man.entrypoint.MapGoogler")
@mock.patch("traffic_man.entrypoint.keep_running")
@mock.patch("traffic_man.entrypoint.TrafficDateTime")
@mock.patch("traffic_man.entrypoint.sleep", return_value=None)
@mock.patch("traffic_man.entrypoint.DataSetup")
@mock.patch("traffic_man.entrypoint.db")
@mock.patch("traffic_man.entrypoint.metadata_obj")
class Testentrypoint_whileloop(unittest.TestCase):

    ### ------------------------- entrypoint.main() -----------------------------   
    def test_main_while_loop_flag_1201_set(self, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, True)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = None
        main()
        self.assertEqual(mock_mapgoogler.return_value.google_call_with_retry.call_count, 0)


    def test_main_while_loop_no_google_data(self, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = None
        main()
        self.assertEqual(mock_mapgoogler.return_value.google_call_with_retry.call_count, 1)
        self.assertEqual(mock_mapgoogler.return_value.calc_traffic.call_count, 0)

    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_problem_google_calc(self,  mock_traffic_data, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = None
        main()
        self.assertEqual(mock_mapgoogler.calc_traffic.call_count, 1)
        self.assertEqual(mock_traffic_data.return_value.store_traffic_data.call_count, 0)

    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_bad_traffic_already_written(self, mock_traffic_data, mock_config, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .5}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = "traffic"
        main()
        self.assertEqual(mock_traffic_data.return_value.check_traffic_conditions.call_count, 1)
        self.assertEqual(mock_traffic_data.return_value.write_bad_traffic.call_count, 0)

    @mock.patch("traffic_man.entrypoint.SMSData")
    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_bad_traffic_sms_already_sent(self, mock_traffic_data, mock_config, mock_smsdata, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .5}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = None
        mock_smsdata.return_value.check_sms_today.return_value = True
        main()
        self.assertEqual(mock_traffic_data.return_value.write_bad_traffic.call_count, 1)
        self.assertEqual(mock_smsdata.return_value.check_sms_today.call_count, 1)
        self.assertEqual(mock_smsdata.return_value.write_sms_record.call_count, 0)

    @mock.patch("traffic_man.entrypoint.TwilioSender")
    @mock.patch("traffic_man.entrypoint.SMSData")
    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_bad_traffic_send_sms(self, mock_traffic_data, mock_config, mock_smsdata, mock_twilio, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .5}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = None
        mock_smsdata.return_value.check_sms_today.return_value = False
        main()
        self.assertEqual(mock_smsdata.return_value.write_sms_record.call_count, 1)



    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_bad_traffic_resolved_already_written(self, mock_traffic_data, mock_config, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .24}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = "traffic_resolved"
        main()
        self.assertEqual(mock_traffic_data.return_value.check_traffic_conditions.call_count, 1)
        self.assertEqual(mock_traffic_data.return_value.write_traffic_resolved.call_count, 0)

    @mock.patch("traffic_man.entrypoint.SMSData")
    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_traffic_resolved_sms_already_sent(self, mock_traffic_data, mock_config, mock_smsdata, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .24}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = "traffic"
        mock_smsdata.return_value.check_sms_today.return_value = True
        main()
        self.assertEqual(mock_traffic_data.return_value.write_traffic_resolved.call_count, 1)
        self.assertEqual(mock_smsdata.return_value.check_sms_today.call_count, 1)
        self.assertEqual(mock_smsdata.return_value.write_sms_record.call_count, 0)

    @mock.patch("traffic_man.entrypoint.TwilioSender")
    @mock.patch("traffic_man.entrypoint.SMSData")
    @mock.patch("traffic_man.entrypoint.Config")
    @mock.patch("traffic_man.entrypoint.TrafficData")
    def test_main_while_loop_traffic_resolved_send_sms(self, mock_traffic_data, mock_config, mock_smsdata, mock_twilio, mock_meta_obj, mock_db, mock_datasetup, mock_sleep, mock_trafficdatetime, mock_run, mock_mapgoogler):
        mock_datasetup.return_value.update_check_times.return_value = True
        mock_datasetup.return_value.update_holidays.return_value = True
        mock_datasetup.return_value.update_check_days.return_value = True
        mock_datasetup.return_value.update_phone_numbers.return_value = True

        mock_trafficdatetime.return_value.get_next_run_sleep_seconds.return_value = (10, False)

        mock_run.side_effect = [True, False] # make sure we only cycle through the while loop routine once

        mock_mapgoogler.return_value.google_call_with_retry.return_value = {"fake google data": "fake data"}
        mock_mapgoogler.calc_traffic.return_value = {"traffic_ratio": .24}

        mock_config.overage_parameter = .5

        mock_traffic_data.return_value.check_traffic_conditions.return_value = "traffic"
        mock_smsdata.return_value.check_sms_today.return_value = False
        main()
        self.assertEqual(mock_smsdata.return_value.write_sms_record.call_count, 1)