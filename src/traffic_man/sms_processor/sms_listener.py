from traffic_man.config import Config

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.setLevel(Config.log_level)
logger.addHandler(Config.file_handler)
logger.addHandler(Config.stout_handler)


class SMSListener:
    
    @staticmethod
    def get_message(redis_conn, redis_stream_key, redis_consumer_grp, consumer_name, msg_read_count, block_time_ms, inbound_sms_q, kill_q):
        
        while kill_q.empty():
            streams = redis_conn.xreadgroup(groupname=redis_consumer_grp, consumername=consumer_name, streams={redis_stream_key: ">"}, count=msg_read_count, block=block_time_ms)
        
            if streams:
                logger.info("{0} messages retrieved from redis stream {1}".format(len(streams[0][1]), streams[0][0]))
                
                # loop through the messages and post them to the inbound sms queue, acknowledge the message with redis, and delete the message from the stream
                for msg in streams[0][1]:
                    logger.debug("posting this message to the sms_inbound_q: {0}".format(msg[1]))
                    inbound_sms_q.put(msg[1])

                    logger.debug("acknowledging message id in redis stream: {0}".format(msg[0]))
                    redis_conn.xack(redis_stream_key, redis_consumer_grp, msg[0])

                    logger.debug("deleting message from redis stream: {0}".format(msg[0]))
                    redis_conn.xdel(redis_stream_key, msg[0])