import requests
from string import Template
from requests.exceptions import HTTPError
import json
import os
import logging
import pandas as pd
import OnaHelper
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()

username = getenv('ONA_USERNAME')
password = getenv('ONA_PASSWORD')
tokenJsonFile = getenv('TOKEN_JSON')
log_level = getenv('LOG_LEVEL', 'INFO')

db_file = 'ona_form.db'
all_form_list = 'allFormList.txt'
form_list_file = 'formList.txt'
json_form_list_file = 'jsonFormList.txt'

rootUrl = "https://api.ona.io"
# logLevel = logging.DEBUG if CONFIG['log_debug_messages'] else logging.INFO
logfile = path.join(path.dirname(path.abspath(__file__)), "ona_download.log")
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    handlers=[logging.FileHandler(logfile, 'w', 'utf-8')],
                    level=log_level)

onaToken = ""
payload = ""
helper = OnaHelper.OnaHelper(username=username, password=password, baseurl=rootUrl, db_file=db_file)

logging.debug(f'Using the following credentials username: {username}')

data = json.loads("{}")


def fetch_media_files(form_id, form_name, page_number):
    try:
        logging.info(f'Pulling attachments for {form_id}')
        data_resp = helper.download_form_attachments(form_id, payload="", headers=headers,
                                                     page_no=page_number, page_size=50, media_type="image")
        for form in data_resp:
            dir = f'downloads/images/{form_name}/page_{page_number}'
            if not os.path.exists(dir):
                os.mkdir(dir)
            file_name = form["id"]
            attachment_url = form["download_url"]
            filename = form["filename"]
            data = filename.split('.')
            extension = data[1]

            # logging.info(f'Filename is {filename} and extension is {extension}-------->')
            logging.info(f'Downloading attachment is {extension} and extension is {attachment_url}-------->')
            helper.download_attachment(file_name=file_name, url=attachment_url,
                                       extension=extension, page_no=page_number)

    except Exception as ex:
        logging.error(f'Unable to download attachments: {ex}', exc_info=True)


try:
    try:
        with open(tokenJsonFile) as json_file_obj:
            data = json.load(json_file_obj)
    except Exception as fileErr:
        logging.error(f'Error reading {tokenJsonFile} file {fileErr}', exc_info=True)
    # next sequence here
    if "api_token" in data:
        onaToken = data['api_token']
    else:
        logging.info("No api token, requesting a new one")
        onaToken = helper.refresh_token(tokenJsonFile)
    if onaToken:
        headers = {'authorization': 'Token ' + onaToken}
        logging.debug(f'Found valid api token -> proceeding to fetch form metadata')
        # Loop through certain range to denote number of pages
        for x in range(1, 501, 1):
            logging.info(f'Fetching data in Page number {x}')
            fetch_media_files("337918", "Score_Weed_Control_AC", page_number=x)
    else:
        logging.warning('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    logging.critical(f'Unable to read json file {err}', exc_info=True)
