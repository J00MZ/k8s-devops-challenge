#!/usr/bin/env python

import argparse
import coloredlogs
import crawltricks

if __name__ == "__main__":
    coloredlogs.install(level='DEBUG', isatty=True)
    parser = argparse.ArgumentParser(description='A simple web crawler implementation')
    parser.add_argument('-u', '--url', help="Main URL to start crawling from", required=True)
    parser.add_argument('-d', '--depth', help="Depth to crawl", required=True, type=int)
    args = parser.parse_args()
    crawl = crawltricks.Crawler(args)

    crawl.init_crawl()
    