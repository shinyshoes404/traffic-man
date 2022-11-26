import sqlalchemy as db

from traffic_man.db.models import check_times, holidays, check_days
from traffic_man.config import Config
from datetime import datetime, timedelta
import logging

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


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

        # if it's not a weekday that we check traffic, just return seconds until tomorrow
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