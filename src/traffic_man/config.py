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
    # don't do debug level if running in a prod environament
    if os.environ.get("TRAFFIC_MAN_LOG_LEVEL") == "debug" and os.environ.get("TRAFFIC_MAN_ENV") == "dev":
        set_log_level = logging.DEBUG
    else:
        set_log_level = logging.INFO

    log_path = os.path.join(etc_basedir, "traffic-man.log")
    log_level = set_log_level
    log_format = logging.Formatter(" %(asctime)s - [%(levelname)s] - %(name)s - %(threadName)s - %(message)s", "%Y-%m-%d %H:%M:%S %z")
    log_maxbytes = 5000000
    log_backup_count = 1

    file_handler = RotatingFileHandler(log_path, maxBytes=log_maxbytes, backupCount=log_backup_count) 
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)

    stout_handler = logging.StreamHandler(sys.stdout)
    stout_handler.setLevel(log_level)
    stout_handler.setFormatter(log_format)

    # Logging setup
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(stout_handler)

    ### -- GOOGLE MAPS PARAMETERS --- ###
    # indicates the traffic model you want to use in the request to sent to Google Maps API
    if os.environ.get("GOOGLE_MAPS_TRAFFIC_MODEL") == "pessimistic":        
        traffic_model = "pessimistic"
        logger.info("google maps traffic model param set to: {0}".format(traffic_model))
    elif os.environ.get("GOOGLE_MAPS_TRAFFIC_MODEL") == "optimistic":
        traffic_model = "optimistic"
        logger.info("google maps traffic model param set to: {0}".format(traffic_model))
    else:
        traffic_model = "best_guess"
        logger.info("google maps traffic model param set to: {0}".format(traffic_model))
    


    # the mode you want to use when sending the request to the Google Maps API
    if os.environ.get("GOOGLE_MAPS_MODE") == "walking":
        mode = "walking"
        logger.info("google maps mode param set to: {0}".format(mode))
    elif os.environ.get("GOOGLE_MAPS_MODE") == "bicycling":
        mode = "bicycling"
        logger.info("google maps mode param set to: {0}".format(mode))
    elif os.environ.get("GOOGLE_MAPS_MODE") == "transit":
        mode = "transit"
        logger.info("google maps mode param set to: {0}".format(mode))
    else:
        mode = "driving"
        logger.info("google maps mode param set to: {0}".format(mode))

    # the language you want Google to use in its API response
    language = "en"
    logger.info("google language param defaulting to: {0}".format(language))

    ### --- TRAFFIC_MAN_PARAMS --- ###
    # traffic overage parameter
    try:
        overage_parameter = float(os.environ.get("TRAFFIC_MAN_OVERAGE_PARAM"))
        logger.info("traffic man overage parameter set to: {0}".format(overage_parameter))
    except:        
        overage_parameter = 0.1
        logger.info("traffic man overage parameter defaulting to: {0}".format(overage_parameter))

    # times to check traffic conditions
    try:
        traffic_check_times = os.environ.get("TRAFFIC_MAN_CHECK_TIMES").split("|")
        logger.info("traffic man check times set to: {0}".format(traffic_check_times))

    except:
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
                                "19:00",
                                "19:15",
                                "19:30"
                                ]

        logger.info("traffic man check times defaulting to: {0}".format(traffic_check_times))

    # days you don't want to check traffic, because it is a holiday
    try:
        holidays = os.environ.get("TRAFFIC_MAN_HOLIDAYS").split("|")
        logger.info("traffic man holidays param set to: {0}".format(holidays))
    except:
        holidays =  [
                    "2022-12-26",
                    "2023-01-02",
                    "2023-05-29",
                    "2023-07-04",
                    "2023-09-04",
                    "2023-11-23",
                    "2023-12-25",
                    "2024-01-01",
                    "2024-05-27",
                    "2024-07-04",
                    "2024-09-02",
                    "2024-11-28",
                    "2024-12-25",
                    "2025-01-01"

                    ]
        logger.info("traffic man holidays param defaulted to: {0}".format(holidays))

    # days of the week to check traffic
    try:
        traffic_check_days = os.environ.get("TRAFFIC_MAN_CHECK_DAYS").split("|")
        logger.info("traffic man check days set to: {0}".format(traffic_check_days))
    except:
        traffic_check_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        logger.info("traffic man check days param defaulted to: {0}".format(traffic_check_days))