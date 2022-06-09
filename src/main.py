from traffic_man import engine
from traffic_man.db_ops import DataSetup, TrafficDateTime, TrafficData
from traffic_man.google import MapGoogler
from traffic_man.config import Config
from traffic_man.twilio import TwilioSender
from time import sleep

data_setup = DataSetup(engine)
data_setup.update_check_times()
data_setup.update_holidays()
data_setup.update_check_days()
data_setup.update_phone_numbers()

while True:
    traffic_date = TrafficDateTime(engine)

    sleep_seconds = traffic_date.get_next_run_sleep_seconds()
    print("sleeping for {0} seconds".format(sleep_seconds))
    sleep(sleep_seconds)

    raw_maps_data = MapGoogler.call_google_maps()
    if raw_maps_data == None:
        sleep(10)
        raw_maps_data = MapGoogler.call_google_maps()
    
    maps_data_tranformed = MapGoogler.calc_traffic(raw_maps_data)
    traffic_data = TrafficData(engine)
    traffic_data.store_traffic_data(maps_data_tranformed)

    if maps_data_tranformed["traffic_ratio"] >= Config.overage_parameter:        
        traffic_condition = traffic_data.check_traffic_conditions()
        if traffic_condition == None:
            traffic_data.write_bad_traffic()
            twilio_sender = TwilioSender()                        
            twilio_sender.send_bad_traffic_sms(traffic_data.get_phone_numbers())
    
    elif maps_data_tranformed["traffic_ratio"] < (Config.overage_parameter * 0.5):
        traffic_condition = traffic_data.check_traffic_conditions()
        if traffic_condition == "traffic":
            traffic_data.write_traffic_resolved()
            twilio_sender = TwilioSender()
            twilio_sender.send_resolved_traffic_sms(traffic_data.get_phone_numbers())

