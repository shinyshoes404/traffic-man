import sqlalchemy as db

from traffic_man.models import check_times, holidays, phone_numbers, check_days, traffic_data, traffic_conditions
from traffic_man.config import Config
from datetime import datetime, timedelta
import os



class DataSetup:
    def __init__(self, engine):
        self.engine = engine

    def update_check_times(self):

        # clear data from the check_times table
        qry = db.delete(check_times)
        with self.engine.connect() as connection:
            connection.execute(qry)

        # populate times from Config
        for time in Config.traffic_check_times:            
            qry = check_times.insert().values(time=time)
            with self.engine.connect() as connection:
                connection.execute(qry)


    def update_holidays(self):

        # clear data from the holidays table
        qry = db.delete(holidays)
        with self.engine.connect() as connection:
            connection.execute(qry)
        
        # populate holidays from Config
        for date in Config.holidays:
            qry = holidays.insert().values(date=date)
            with self.engine.connect() as connection:
                connection.execute(qry)
    
    def update_check_days(self):

        # clear data from the check_days table
        qry = db.delete(check_days)
        with self.engine.connect() as connection:
            connection.execute(qry)
        
        # populate days to check
        for day_of_week in Config.traffic_check_days:
            qry = check_days.insert().values(check_days=day_of_week)
            with self.engine.connect() as connection:
                connection.execute(qry)
    
    def update_phone_numbers(self):
        
        # clear data from the phone_numbers table
        qry = db.delete(phone_numbers)
        with self.engine.connect() as connection:
            connection.execute(qry)
        
        # populate phone numbers
        for number in os.environ.get("PHONE_NUMS").split("|"):
            qry = phone_numbers.insert().values(phone_num=number)
            with self.engine.connect() as connection:
                connection.execute(qry)


class TrafficDateTime:

    def __init__(self, engine):
        self.engine = engine
    
    def _get_1201_tomorrow(self) -> datetime:
        tomorrow_1201 = datetime.strptime(self.curr_date, "%Y-%m-%d") + timedelta(minutes=1441)
        return tomorrow_1201    

    def _check_weekday(self) -> bool:
        # do we need to check for traffic on this day of the week?
        qry = check_days.select().where(check_days.c.check_days == self.curr_weekday)

        with self.engine.connect() as connection:
            results = connection.execute(qry)
            if len(results.fetchall()) == 0:
                return False

        return True
    
    def _check_holiday(self) -> bool:
        # is today a holiday?
        qry = holidays.select().where(holidays.c.date == self.curr_date)
        
        with self.engine.connect() as connection:
            results = connection.execute(qry)
            if len(results.fetchall()) == 0:
                return False
        
        return True
    
    def _get_seconds_to_time(self, next_time):
        seconds_to_sleep = (datetime.strptime(self.curr_date + " " + next_time, "%Y-%m-%d %H:%M") - self.curr_datetime).total_seconds()
        return seconds_to_sleep

    def _check_next_time(self) -> str:
        qry = db.select(db.func.min(check_times.c.time)).where(check_times.c.time > self.curr_hr_min)
        with self.engine.connect() as connection:
            results = connection.execute(qry)
            data = results.fetchone()
            if len(data) == 0:
                return None

        return data[0]

    def get_next_run_sleep_seconds(self) -> int:
        self.curr_datetime = datetime.now()
        self.curr_hr_min = self.curr_datetime.strftime("%H:%M")
        self.curr_date = self.curr_datetime.strftime("%Y-%m-%d")
        self.curr_weekday = self.curr_datetime.strftime("%A").lower()

        # if it not a weekday that we check traffic, just return seconds until tomorrow
        if self._check_weekday() == False:
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep
        
        # if it is a holiday, just return the seconds until tomorrow
        if self._check_holiday() == True:
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep
        
        next_time = self._check_next_time()

        if next_time == None:
            seconds_to_sleep = int((self._get_1201_tomorrow() - datetime.now()).total_seconds())
            return seconds_to_sleep
        
        # if no other matches get the number of seconds until the next run
        seconds_to_sleep = self._get_seconds_to_time(next_time)
        return seconds_to_sleep


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
            print(e)
            return False
        
        return True

    def check_traffic_conditions(self) -> str:
        qry = traffic_conditions.select().where(traffic_conditions.c.date == self.curr_date)
        with self.engine.connect() as connection:
            results = connection.execute(qry)
            row = results.fetchall()

        if len(row) == 0:
            return None
        
        if row[0][3]:
            return "traffic_resolved"
        else:
            return "traffic"
    
    def write_bad_traffic(self):
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        qry = traffic_conditions.insert().values(date=self.curr_date, bad_traffic_datetime=curr_datetime)
        with self.engine.connect() as connection:
            connection.execute(qry)
    
    def write_traffic_resolved(self):
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        qry = traffic_conditions.update().where(traffic_conditions.c.date == self.curr_date).values(resolve_traffic_datetime=curr_datetime)
        with self.engine.connect() as connection:
            connection.execute(qry)
    
    def get_phone_numbers(self):
        qry = db.select([phone_numbers.c.phone_num])
        print(qry)
        with self.engine.connect() as connection:
            result_obj = connection.execute(qry)
            results_data = result_obj.fetchall()
        
        phone_nums = []

        for num in results_data:
            phone_nums.append(num[0])
        
        return phone_nums
        
    

