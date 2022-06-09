from configparser import ConfigParser
import os, platform, logging, sys
from logging.handlers import RotatingFileHandler


class Config:

    ### -- WHERE TO FIND FILES --- ###
    if os.environ.get("TRAFFIC_MAN_ENV") == "dev":
        etc_basedir = os.path.abspath(os.path.dirname(__file__))
        etc_basedir = os.path.join(etc_basedir, '../../')
    
    else:
        if platform.system() == "Linux":
            etc_basedir = '/etc/traffic-man'
        elif platform.system() == "Windows":
            etc_basedir = "C:\\Users\\" + os.getlogin() + "\\.traffic-man"
  
    db_path = os.path.join(etc_basedir, "traffic_man.db")


    ### --- LOG PARAMETERS --- ###
    log_path = os.path.join(etc_basedir, "traffic-man.log")
    log_level = logging.INFO
    log_format = logging.Formatter(" %(asctime)s - [%(levelname)s] - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S %z")
    log_maxbytes = 5000000
    log_backup_count = 1

    file_handler = RotatingFileHandler(log_path, maxBytes=log_maxbytes, backupCount=log_backup_count) 
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)

    stout_handler = logging.StreamHandler(sys.stdout)
    stout_handler.setLevel(log_level)
    stout_handler.setFormatter(log_format)


    ### -- GOOGLE MAPS PARAMETERS --- ###

    # indicates the traffic model you want to use in the request to sent to Google Maps API
    traffic_model = "best_guess"
    # the mode you want to use when sending the request to the Google Maps API
    mode = "driving"
    # the language you want Google to use in its API response   
    language = "en"

    ### --- TRAFFIC_MAN_PARAMS --- ###

    # traffic overage parameter
    overage_parameter = 0.5

    # times to check traffic condition
    traffic_check_times = [
                            "16:00", 
                            "16:15",
                            "16:30",
                            "16:45",
                            "17:00",
                            "17:15",
                            "17:30",
                            "17:45",
                            "18:00",
                            "18:15",
                            "18:30",
                            "18:45",
                            "19:00"
                            ]


    # days you don't want to check traffic, because it is a holiday
    holidays =  [
                "2022-07-04",
                "2022-09-05",
                "2022-11-24",
                "2022-12-26"
                ]

    # days of the week to check traffic
    traffic_check_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]