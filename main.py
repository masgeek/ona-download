import requests
from string import Template
from requests.exceptions import HTTPError
import json
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

print(f'Using the following credentials username: {username} and password: xxxxxx sucker!!!!')

data = json.loads("{}")

try:
    try:
        with open(tokenJsonFile) as json_file_obj:
            data = json.load(json_file_obj)
    except Exception as fileErr:
        # logging.error(f'Error reading {tokenJsonFile} file {fileErr}', exc_info=True)
        logging.exception("Unable to read file")
    # next sequence here
    if "api_token" in data:
        onaToken = data['api_token']
    else:
        logging.info("No api token, requesting a new one")
        onaToken = helper.refresh_token(tokenJsonFile)
    if onaToken:
        headers = {'authorization': 'Token ' + onaToken}
        logging.debug(f'Found valid api token -> proceeding to fetch from metadata')
        resp = helper.fetch_form_data(payload="", headers=headers)
        if resp == 200:
            form_id_list = helper.read_form_list(json_form_list_file)
            for form in form_id_list:
                # Now we query the data
                form_id = form[0]
                form_name = form[1]
                json_file = f'downloads/json/{form_name}.json'
                file_name = f'downloads/csv/{form_name}.csv'
                tagFile = open(file_name, 'w', newline='', encoding='utf-8')
                try:
                    logging.info(f'Pulling submission for {form_name}')
                    data_resp = helper.download_csv_form_data(form_id, payload="", headers=headers)

                    logging.info(f'Response is {data_resp}')
                    tagFile.write(data_resp)
                except Exception as err:
                    logging.error(f'Unable to write CSV {form_name} for: {err}', exc_info=True)
                finally:
                    tagFile.close()

    else:
        logging.warning('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    logging.critical(f'Unable to read json file {err}', exc_info=True)
