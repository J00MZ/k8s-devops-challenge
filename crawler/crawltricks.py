#!/usr/bin/env python

import argparse
import requests
import requests_html
from requests_html import HTMLSession
import logging
import os
import time
import magic
import csv
import unicodedata
import string
import urllib
from urllib.parse import urlparse
from urllib.parse import quote
import redis
import concurrent.futures

class Crawler(object):
    
    def __init__(self, args):
        self._root_url = args.url
        self._depth = args.depth
        self._logger = logging.getLogger('crawlogger')
        self._redis_cache = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
        self._root_dir = self.make_directory()

    def init_crawl(self):
        url = self._root_url
        root_depth = self._depth
        start_time = round(time.time(),5)

        if root_depth <= 0:
            self._logger.error(f"Depth {root_depth} is not sufficient.")
            exit(1)
        
        self._logger.info(f"Starting crawl of URL [{url}] until depth [{root_depth}] at [{time.strftime('%X %x %Z')}]")
        root_filename = self.get_page(url)

        if not self.is_html(os.path.join(self._root_dir, root_filename)):
            self._logger.error(f"URL {url} is not of type 'text/html', will not start crawl.")
            exit(1)
        self._logger.info(f"URL {url} is type 'text/html'! let's go..")
        # for initial page, create key, calculate ratio, insert to cache
        root_ratio = self.calc_ratio(url)
        url_as_key = self.clean_filename(url)
        root_key = f"{self._root_dir}:{url_as_key}"
        if not self._redis_cache.exists(root_key):
            self._logger.info(f"Creating crawl ID [{root_key}]")
            self._redis_cache.hmset(root_key, {"url": url, "depth": 0, "ratio": root_ratio})
        
        # Main logic
        self.start_crawling(url, root_depth)
        # Ends here!
        duration = round(time.time() - start_time, 3)
        self.print_tsv()
        self._logger.info(f"Ended crawl of depth [{root_depth}], on URL [{url}] at [{time.strftime('%X %x %Z')}]. took {duration} seconds")

    def start_crawling(self, url, depth):
        root_depth = self._depth
        height = int(depth)
        current_depth = root_depth - height
        
        if url is not self._root_url:
            # Check if we have file already
            url_key = f"{self._root_dir}:{self.clean_filename(url)}"
            if self.url_in_cache(url_key):
                self._logger.warn(f"URL [{url}] has been already processed, details are cached.")            
            else:
                filename = self.get_page(url)
            
            if self.is_html(os.path.join(self._root_dir, filename)):
                self._logger.info(f"URL [{url}] is type 'text/html'! let's go..")
            else:
                self._logger.warn(f"URL [{url}] is not of type 'text/html'")
                return # does not err, since we want to continue to other links recursively

        # recursion stop condition
        if height > 0:
            self._logger.info(f"Processing URL [{url}] at depth [{current_depth}]")
            all_page_links = HTMLSession().get(url).html.absolute_links
            # speed up program by parallelizing all links
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_url = {executor.submit(self.start_crawling, link, height - 1): link for link in all_page_links}
                for future in concurrent.futures.as_completed(future_to_url):
                    self._logger.debug(f"Completed thread.")   
        else:
            if url is not self._root_url:
                ratio = self.calc_ratio(url)
                url_as_key = self.clean_filename(url)
                self.write_to_cache(url_as_key, url, current_depth, ratio)
                self._logger.info(f"wrote key {url_as_key} ['ratio':'{ratio}'] to redis")

    def make_directory(self):
        parsed_url = urlparse(self._root_url)
        dir_name = parsed_url.netloc
        try:
            os.mkdir(dir_name)
            self._logger.info(f"Directory {dir_name} created.")
        except FileExistsError:
            self._logger.warn(f"Directory {dir_name} already exists. will write to existing directory.")
        return dir_name
    
    def url_in_cache(self, key):
        return self._redis_cache.exists(key)

    def is_html(self, filename):
        self._logger.info(f"Checking if file [{filename}] is of type 'text/html'")
        kind = magic.from_file(filename, mime=True)
        return kind in 'text/html'

    def get_page(self, url):
        sanitized_filename = self.clean_filename(url)
        filename = os.path.join(self._root_dir, sanitized_filename)
        if not os.path.isfile(filename):
            page = requests.get(url).content.decode('utf-8')
            with open(filename, "w") as file:
                file.write(page)
                self._logger.info(f"File {sanitized_filename} created.")
        else:
            self._logger.warn(f"File {sanitized_filename} already exists.")
        return sanitized_filename

    def clean_filename(self, url, replace=' '):
        whitelist = "-_.() %s%s" % (string.ascii_letters, string.digits)
        char_limit = 255
        for r in replace:
            filename = url.replace(r,'_')      
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
        cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
        if len(cleaned_filename) > char_limit:
            self._logger.warn(f"Filename truncated because it was over {char_limit}. Filename {cleaned_filename} may no longer be unique.")
        return cleaned_filename[:char_limit]  

    def calc_ratio(self, url):
        session = HTMLSession()
        r = session.get(url)
        all_links = r.html.absolute_links
        domain_links = self.count_domain_links(all_links, urlparse(url))
        total_links = len(all_links)
        if total_links > 0:
            ratio = float(round(domain_links/total_links,2))
            self._logger.info(f"The ratio for [{url}] is [{ratio}]")
        else:
            ratio = 0
            self._logger.warn(f"no links in this page, ratio for [{url}] is [{ratio}]")

        return ratio

    def count_domain_links(self, links, url):
        domain = url.netloc
        return len([link for link in links if domain in link])

    def print_tsv(self):
        self._logger.info(f"printing [{self._root_url}] crawl results to TSV file")
        col_names = ['url', 'depth', 'ratio']    
        
        with open(os.path.join(self._root_dir, "output.tsv"), 'w', newline='') as tsv_file:
            tsv_output = csv.writer(tsv_file, delimiter='\t')
            tsv_output.writerow(col_names)
            tsv_output.writerows(self.dump_all_cache_data())   
    
    def write_to_cache(self, url_as_key, url, depth, ratio):
        cache = self._redis_cache
        cache.hmset(f"{self._root_dir}:{url_as_key}", {"url": url, "depth": depth, "ratio": ratio})

    def dump_all_cache_data(self):
        all_data = []
        cols = ["url","depth", "ratio"]
        for key in self._redis_cache.keys(pattern=f"{self._root_dir}*"):
            if int(self._redis_cache.hget(key, 'depth')) <= self._depth:
                all_data.append(self._redis_cache.hmget(key, cols))
                self._logger.debug(f"got key {key}")
        self._logger.warn(f"Got {len(all_data)} entries for crawl [{self._root_dir}] depth {self._depth}")
        return all_data
        