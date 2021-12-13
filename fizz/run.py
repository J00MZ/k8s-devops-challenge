#!/usr/bin/env python3

import os
import time
import datetime
import json
from random import randint


def main():
    for x in range(100):
        fb = randint(1,102)
        
        for fizzbuzz in range(1,fb):
            date_now = datetime.datetime.now().isoformat()
            print(f'at {date_now} - fizzbuzz checking: {fizzbuzz}')
            if fizzbuzz % 15 == 0:
                print("fizzbuzz!")
                continue
            elif fizzbuzz % 3 == 0:
                print("fizz")
                continue
            elif fizzbuzz % 5 == 0:
                print("buzz")
                continue
            else:
                print(fizzbuzz)
        
        sleepytime = fb%5 #dont sleep too long on the job, max 5 seconds.
        print(f'sleeping for {sleepytime} seconds between fizzbuzz checks.')
        time.sleep(sleepytime)

if __name__ == "__main__":
    main()
