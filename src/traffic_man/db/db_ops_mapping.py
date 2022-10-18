# defining how directives provided by outside processes via msg queue map to
# database operation functions in db_ops

from traffic_man.db.traffic_date_time import TrafficDateTime
from traffic_man.db.traffic_data import TrafficData
from traffic_man.db.sms_data import SMSData
from traffic_man.db.users import UserData

db_ops_mapping = {
    "GET_SECONDS_TO_NEXT_RUN" : {"class": TrafficDateTime, "method": TrafficDateTime.get_next_run_sleep_seconds},
    "STORE_TRAFFIC_DATA": {"class": TrafficData, "method": TrafficData.store_traffic_data},
    "CHECK_TRAFFIC_CONDITIONS": {"class": TrafficData, "method": TrafficData.check_traffic_conditions},
    "WRITE_BAD_TRAFFIC": {"class": TrafficData, "method": TrafficData.write_bad_traffic},
    "WRITE_TRAFFIC_RESOLVED": {"class": TrafficData, "method": TrafficData.write_traffic_resolved},
    "GET_SMS_LIST_BY_TYPE": {"class": SMSData, "method": SMSData.check_sms_today},
    "WRITE_SMS_RECORDS": {"class": SMSData, "method": SMSData.write_sms_records},
    "GET_ORIG_DEST_PAIRS" : {"class": UserData, "method": UserData.get_orig_dest_pairs},
    "GET_SUB_PHONE_NUMS_BY_ORIG_DEST": {"class": UserData, "method": UserData.get_sub_phone_numbers_by_orig_dest_pair}
}