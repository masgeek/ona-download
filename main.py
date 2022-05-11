import json
import logging
import logging.config
import OnaHelper
from os import getenv, path
from dotenv import load_dotenv
import yaml
import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--format', '-fmt', help='Format to download the file in', type=str, default='json')
parser.add_argument('--mode', '-m', help='Format to download the file in', type=str, default='INFO')
parser.add_argument('--user', '-u', help='Define user to download file', type=str, default='mtariku')
parser.add_argument('--password', '-p', help='User password', type=str)
parser.add_argument('--file', '-f',
                    help='Specify which txt file has the list of forms to process (formList.txt,sandman.txt)', type=str,
                    default='formList.txt')

args = parser.parse_args()

load_dotenv()

username = args.user
password = args.password
fileFormat = args.format
tokenJsonFile = f'{username}.json'
log_level = args.mode

db_file = 'ona_form.db'
all_form_list = args.file

rootUrl = "https://api.ona.io"

logfileError = path.join(path.dirname(path.abspath(__file__)), "logs/errors.log")
logfileInfo = path.join(path.dirname(path.abspath(__file__)), "logs/info.log")

c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(logfileError, 'w', 'utf-8')
f_info_handler = logging.FileHandler(logfileInfo, 'w', 'utf-8')
c_handler.setLevel(logging.DEBUG)
f_info_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    handlers=[c_handler, f_handler, f_info_handler],
                    level=log_level)

onaToken = ""
payload = ""

helper = OnaHelper.OnaHelper(username=username, password=password, baseurl=rootUrl, db_file=db_file, my_logger=logging)

logging.info(f'Using the following credentials username: {username}')

data = json.loads("{}")


def fetch_json_data(form_id_list):
    try:
        for form in form_id_list:
            # Now we query the data
            form_id = form[0]
            form_name = form[1]
            json_file = f'downloads/json/{form_name}.json'
            try:
                logging.info(f'Pulling submission for {form_name}')
                data_resp = helper.download_json_form_data(form_id, payload="", headers=headers)
                logging.info(f'Form {form_name} has {len(data_resp)} submissions')
                with open(json_file, 'w') as json_file_wr:
                    json.dump(data_resp, json_file_wr, indent=4)
            except Exception as errEx:
                logging.error(f'Unable to write JSON {form_name} for: {errEx}', exc_info=True)
    except Exception as ex:
        logging.error(f'Unable to download JSON: {ex}', exc_info=True)


def fetch_csv_data(form_id_list):
    try:
        for form in form_id_list:
            # Now we query the data
            form_id = form[0]
            form_name = form[1]
            json_file = f'downloads/json/{form_name}.{fileFormat}'
            save_path = f'downloads/converted/{form_name}.{fileFormat}'
            logging.info(f'Pulling submission for {form_name} save at {save_path}')
            data_resp = helper.download_csv_form_data(form_id, payload="", headers=headers, download_format=fileFormat,
                                                      file_name=save_path)

    except Exception as ex:
        logging.error(f'Unable to download CSV: {ex}', exc_info=True)


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
        resp = helper.fetch_form_data(payload="", headers=headers)  # fetch list of forms
        if resp == 200:
            json_form_list = helper.read_form_list(all_form_list)
            if fileFormat == 'json':
                fetch_json_data(json_form_list)
            else:
                fetch_csv_data(json_form_list)

    else:
        logging.warning('Unable to fetch token, please check your connection -> Exiting now :-(')

except FileNotFoundError as err:
    logging.critical(f'Unable to read json file {err}', exc_info=True)
