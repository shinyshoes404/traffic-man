from traffic_man import engine
from traffic_man.db_ops import DataSetup, TrafficDate
from time import sleep

data_setup = DataSetup(engine)
data_setup.update_check_times()
data_setup.update_holidays()
data_setup.update_check_days()
data_setup.update_phone_numbers()

while True:
    traffic_date = TrafficDate(engine)

    sleep_seconds = traffic_date.get_next_run_sleep_seconds()
    print("sleeping for {0} seonds".format(sleep_seconds))
    sleep(sleep_seconds)

    
