#!/usr/bin/env python

import os
import time
import datetime
import logging
import logging.config
import json
import redis
from redis import Redis
from random import randint


def main():
    with open("/app/log_config.json", 'r') as log_conf_file:
        config_dict = json.load(log_conf_file)

    logging.config.dictConfig(config_dict)

    # Log that the logger was configured
    logger = logging.getLogger(__name__)
    logger.info('intialized logger()!')

    redis_db = get_redis()

    for x in range(1000):
        fb = randint(1,1024)
        
        for fizzbuzz in range(1,fb):
            s = datetime.datetime.now().isoformat()
            if fizzbuzz % 3 == 0 and fizzbuzz % 5 == 0:
                logger.warning("Oh No! fizzbuzz")
                logger.info("Yep, it's fizzbuzz")
                logger.debug('Debugging fizzbuzz...')
                continue
            elif fizzbuzz % 3 == 0:
                logger.warning('no worries, just fizz')
                logger.info("Yep, fizzly fizz")
                logger.debug('Debugging fizz...')
                continue
            elif fizzbuzz % 5 == 0:
                logger.warning('got a big buzz!')
                logger.info("Yep, buzz")
                logger.debug('Debugging buzz...')
                continue
            print("at %s - fizzbuzz checking: %s" %(s, fizzbuzz))
            redis_db.set(s,fizzbuzz)
        
        sleepytime = fb%5 #dont sleep too long on the job, max 5 seconds.
        print "sleeping for %s seconds" %(sleepytime)
        time.sleep(sleepytime)

def get_redis():
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    return r

if __name__ == "__main__":
    main()