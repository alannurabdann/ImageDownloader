#! /usr/bin/env python3

import csv
import shutil
import sys
import time
import os
import logging

# http client configuration
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'

# logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

python_version = sys.version_info.major
logging.info("executed by python %d" % python_version)

# define image counter var
COUNT = 0

# compatability with python 2
if python_version == 3:
    import urllib.parse
    import urllib.request
    urljoin = urllib.parse.urljoin
    urlretrieve = urllib.request.urlretrieve
    quote = urllib.parse.quote

    # configure headers
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', user_agent)]
    urllib.request.install_opener(opener)
else:
    import urlparse
    import urllib
    urljoin = urlparse.urljoin
    urlretrieve = urllib.urlretrieve
    quote = urllib.quote

    # configure headers
    class AppURLopener(urllib.FancyURLopener):
        version = user_agent
    urllib._urlopener = AppURLopener()
	
def count_increment():
    global COUNT
    COUNT = COUNT+1
	
def count_reset():
    global COUNT
    COUNT = 0

def fix_url(url):
    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    return url


def download_csv_row_images(row, dest_dir):
    for key in row:
	    count_increment()
	    image_url = row[key]
	    image_filename = "Image-%s" % COUNT
	    download_image(image_url, dest_dir, image_filename)


def download_image(image_url, dest_dir, image_filename):

    try:
        image_url = fix_url(image_url)
        logging.info("downloading image %s" % COUNT)
        tmp_file_name, headers = urlretrieve(image_url)
        content_type = headers.get("Content-Type")

        if content_type == 'image/jpeg' or content_type == 'image/jpg':
            ext = 'jpg'
        elif content_type == 'image/png':
            ext = 'png'
        elif content_type == 'image/gif':
            ext = 'gif'
        elif content_type == 'image/webp':
            ext = 'webp'
        else:
            logging.warning("unknown image content type %s" % content_type)
            return

        image_path = os.path.join(dest_dir, image_filename+"."+ext)
        shutil.move(tmp_file_name, image_path)
    except Exception as e:
        logging.warning("Image download error. %s" % e)

def get_csv_image_dir(csv_filename):

    base = os.path.basename(csv_filename)
    dir = os.path.splitext(base)[0]

    if not os.path.exists(dir):
        os.makedirs(dir)

    return dir

def download_csv_file_images(filename):

    logging.info("importing data from %s" % filename)

    dest_dir = "D:\images"

    #check whether csv file has utf-8 bom char at the beginning
    skip_utf8_seek = 0
    with open(filename, "rb") as csvfile:
        csv_start = csvfile.read(3)
        if csv_start == b'\xef\xbb\xbf':
            skip_utf8_seek = 3


    with open(filename, "r", encoding="utf8") as csvfile:

        # remove ut-8 bon sig
        csvfile.seek(skip_utf8_seek)

        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            download_csv_row_images(row, dest_dir)

def main(args):

    # filename passde through args
    if len(args) >=2:
        csv_filename = args[1]
        download_csv_file_images(csv_filename)
        logging.info("image download completed")

    else:
        logging.warning("no input file found")

    time.sleep(5)

main(sys.argv)