import sqlalchemy as db

from traffic_man.models import check_times, holidays, phone_numbers, check_days, traffic_data, traffic_conditions, sms_data
from traffic_man.config import Config
from datetime import datetime, timedelta
import os,logging

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)

class DataSetup:
    def __init__(self, engine):
        self.engine = engine

    def update_check_times(self):
        logger.info("deleting all data from the check_time table")
        
        try:
            # clear data from the check_times table
            qry = db.delete(check_times)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from check_times")
            logger.error(e)
            return None

        logger.info("adding this data to the check_times table {0}".format(Config.traffic_check_times))
        try:
            # populate times from Config
            for time in Config.traffic_check_times:            
                qry = check_times.insert().values(time=time)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting times into check_times table")
            logger.error(e)
            return None
        
        return True

    def update_holidays(self):
        logger.info("deleting all data from the holidays table")

        try:
            # clear data from the holidays table
            qry = db.delete(holidays)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from holidays")
            logger.error(e)
            return None
        
        logger.info("adding these dates to the holiday table {0}".format(Config.holidays))

        try:
            # populate holidays from Config
            for date in Config.holidays:
                qry = holidays.insert().values(date=date)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem writing dates to holidays table")
            logger.error(e)
            return None

        return True
    
    def update_check_days(self):
        logger.info("deleting data from check_days table")

        try:
            # clear data from the check_days table
            qry = db.delete(check_days)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from check_days table")
            logger.error(e)
            return None
        
        logger.info("adding these days to the check_days table {0}".format(Config.traffic_check_days))
        try:
            # populate days to check
            for day_of_week in Config.traffic_check_days:
                qry = check_days.insert().values(check_days=day_of_week)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting data to check_days table")
            logger.error(e)
            return None
        
        return True
    
    def update_phone_numbers(self):
        
        logger.info("deleting data from the phone_numbers table")
        # clear data from the phone_numbers table
        try:
            qry = db.delete(phone_numbers)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem deleting data from phone_number table")
            logger.error(e)
            return None
        
        logger.info("adding these phone numbers to the phone_numbers table {0}".format(os.environ.get("PHONE_NUMS").split("|")))
        
        try:
            # populate phone numbers
            for number in os.environ.get("PHONE_NUMS").split("|"):
                qry = phone_numbers.insert().values(phone_num=number)
                with self.engine.connect() as connection:
                    connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting data into the phone_numbers table")
            logger.error(e)
            return None

        return True


class TrafficDateTime:

    def __init__(self, engine):
        self.engine = engine
    
    def _get_1201_tomorrow(self) -> datetime:
        tomorrow_1201 = datetime.strptime(self.curr_date, "%Y-%m-%d") + timedelta(minutes=1441)
        logger.debug("tomorrow at 12:01 AM is {0}".format(tomorrow_1201))
        return tomorrow_1201    

    def _check_weekday(self) -> bool:
        try:
            # do we need to check for traffic on this day of the week?
            qry = check_days.select().where(check_days.c.check_days == self.curr_weekday)

            with self.engine.connect() as connection:
                results = connection.execute(qry)
                if len(results.fetchall()) == 0:
                    logger.info("we don't need to check for traffic on {0}".format(self.curr_weekday))
                    return False
        except Exception as e:
            logger.error("problem checking weekday")
            logger.error(e)
            return None

        logger.info("{0} is a traffic check day".format(self.curr_weekday))
        return True
    
    def _check_holiday(self) -> bool:

        try:
            # is today a holiday?
            qry = holidays.select().where(holidays.c.date == self.curr_date)
            
            with self.engine.connect() as connection:
                results = connection.execute(qry)
                if len(results.fetchall()) == 0:
                    logger.info("today is not listed as a holiday")
                    return False
        except Exception as e:
            logger.error("problem checking holiday")
            logger.error(e)
            return None

        logger.info("today is a holiday")
        return True
    
    def _get_seconds_to_time(self, next_time):
        seconds_to_sleep = (datetime.strptime(self.curr_date + " " + next_time, "%Y-%m-%d %H:%M") - self.curr_datetime).total_seconds()
        return seconds_to_sleep

    def _check_next_time(self) -> str:

        try:
            qry = db.select(db.func.min(check_times.c.time)).where(check_times.c.time > self.curr_hr_min)
            with self.engine.connect() as connection:
                results = connection.execute(qry)
                data = results.fetchall()
                if data[0][0] == None:
                    logger.info("no check time returned, need to check tomorrow")
                    return "tomorrow"
        except Exception as e:
            logger.error("problem checking next run time")
            logger.error(e)
            return None

        logger.info("next time to check is {0}".format(data[0][0]))
        return data[0][0]

    def get_next_run_sleep_seconds(self) -> tuple[int, bool]:
        self.curr_datetime = datetime.now()
        self.curr_hr_min = self.curr_datetime.strftime("%H:%M")
        self.curr_date = self.curr_datetime.strftime("%Y-%m-%d")
        self.curr_weekday = self.curr_datetime.strftime("%A").lower()

        logger.info("Current values \n\t\t\t\t\t\t\t\tcurrent datetime: {0} \n\t\t\t\t\t\t\t\tcurrent hr min: {1} \n\t\t\t\t\t\t\t\tcurrent date: {2} \n\t\t\t\t\t\t\t\tcurrent weekday: {3}".format(self.curr_datetime, self.curr_hr_min, self.curr_date, self.curr_weekday))

        # if it not a weekday that we check traffic, just return seconds until tomorrow
        if self._check_weekday() == False:
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep, True
        
        # if it is a holiday, just return the seconds until tomorrow
        if self._check_holiday() == True:
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep, True
        
        next_time = self._check_next_time()

        if next_time == "tomorrow":
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep, True
        
        # if no other matches get the number of seconds until the next run
        seconds_to_sleep = self._get_seconds_to_time(next_time)

        return seconds_to_sleep, False


class TrafficData:
    def __init__(self, engine):
        self.engine = engine
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
    
    def store_traffic_data(self, traffic_json: dict) -> bool:

        qry = traffic_data.insert().values(
            datetime=traffic_json["datetime"],
            origin_addr=traffic_json["origin_addr"],
            destination_addr=traffic_json["destination_addr"],
            duration_sec=traffic_json["duration_sec"],
            duration_traffic_sec=traffic_json["duration_traffic_sec"],
            traffic_ratio=traffic_json["traffic_ratio"]
            )

        try:
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem storing traffic data")
            logger.error(e)
            return None

        logger.info("stored this traffic data in the traffic_data table {0}".format(traffic_json))
        return True

    def check_traffic_conditions(self) -> str:

        try:
            qry = traffic_conditions.select().where(traffic_conditions.c.date == self.curr_date)
            with self.engine.connect() as connection:
                results = connection.execute(qry)
                row = results.fetchall()
        except Exception as e:
            logger.error("problem checking traffic conditions in the db")
            logger.error(e)
            return False

        if len(row) == 0:
            logger.info("no traffic conditions listed for today")
            return None
        
        if row[0][3]:
            logger.info("the traffic_conditions tables says that traffic is resolved")
            return "traffic_resolved"
        else:
            logger.info("the traffic_conditions table says that there is currently traffic")
            return "traffic"
    
    def write_bad_traffic(self):
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            qry = traffic_conditions.insert().values(date=self.curr_date, bad_traffic_datetime=curr_datetime)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem writing back trafic record")
            logger.error(e)
            return None

        logger.info("successfully wrote a bad traffic record for {0} at {1}".format(self.curr_date, curr_datetime))
        return True
    
    def write_traffic_resolved(self):
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            qry = traffic_conditions.update().where(traffic_conditions.c.date == self.curr_date).values(resolve_traffic_datetime=curr_datetime)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem writing traffic resolved record")
            logger.error(e)
            return None
        
        logger.info("successfully wrote traffic resolved record for {0} at {1}".format(self.curr_date, curr_datetime))
        return True

    def get_phone_numbers(self):

        try:
            qry = db.select([phone_numbers.c.phone_num])
            with self.engine.connect() as connection:
                result_obj = connection.execute(qry)
                results_data = result_obj.fetchall()
        except Exception as e:
            logger.error("problem fetching phone numbers from phone_numbers table")
            logger.error(e)
            return None
        
        phone_nums = []

        for num in results_data:
            phone_nums.append(num[0])
        
        logger.info("got these phone numbers: {0}".format(phone_nums))
        return phone_nums
        
    

class SMSData:
    def __init__(self, engine):
        self.engine = engine
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
    
    def check_sms_today(self, type: str) -> bool:
        try:
            qry = sms_data.select().where(sms_data.c.date == self.curr_date, sms_data.c.sms_type == type)
            with self.engine.connect() as connection:
                result_obj = connection.execute(qry)
                results_data = result_obj.fetchall()
        except Exception as e:
            logger.error("problem getting sms record")
            logger.error(e)
            return None
        
        if len(results_data) == 0:
            logger.info("no sms for {0} sent yet today".format(type))
            return False
        
        logger.info("sms for {0} already sent today".format(type))
        return True
        

    def write_sms_record(self, type: str, err_count: int) -> bool:
        logger.info("attempting to add {0} sms recored for {1}".format(type, self.curr_date))
        try:
            qry = sms_data.insert().values(date=self.curr_date, sms_type=type, err_count=err_count)
            with self.engine.connect() as connection:
                connection.execute(qry)
        except Exception as e:
            logger.error("problem inserting sms sent record")
            logger.error(e)
            return None
        
        return True
