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
all_form_list = 'allFormList.txt'
form_list_file = 'formList.txt'
json_form_list_file = 'jsonFormList.txt'

rootUrl = "https://api.ona.io"

logfile = path.join(path.dirname(path.abspath(__file__)), "ona_download.log")
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    handlers=[logging.FileHandler(logfile, 'w', 'utf-8')],
                    level=log_level)

onaToken = ""
payload = ""
helper = OnaHelper.OnaHelper(username=username, password=password, baseurl=rootUrl, db_file=db_file)

logging.info(f'Using the following credentials username: {username}')

data = json.loads("{}")


def fetch_csv_data(form_id_list):
    try:
        for form in form_id_list:
            # Now we query the data
            form_id = form[0]
            form_name = form[1]
            file_name = f'downloads/csv/{form_name}.csv'
            tagFile = open(file_name, 'w', newline='', encoding='utf-8')
            try:
                logging.info(f'Pulling submission for {form_name}')
                data_resp = helper.download_csv_form_data(form_id, payload="", headers=headers)

                logging.info(f'Response is {data_resp}')
                tagFile.write(data_resp)
            except Exception as err1:
                logging.error(f'Unable to write CSV {form_name} for: {err1}', exc_info=True)
            finally:
                tagFile.close()
    except Exception as ex:
        logging.error(f'Unable to download CSV: {ex}', exc_info=True)


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
                logging.info(f'Response is {data_resp}')
                with open(json_file, 'w') as json_file_wr:
                    json.dump(data_resp, json_file_wr, indent=4)
                # df = pd.read_json(r'' + json_file)

                with open(json_file) as loaded_json_obj:
                    loaded_json = json.load(loaded_json_obj)
                df = pd.json_normalize(loaded_json)

                logging.info(df)
                df.to_csv(rf'downloads/csv/{form_name}.csv')
            except Exception as errEx:
                logging.error(f'Unable to write JSON {form_name} for: {errEx}', exc_info=True)
    except Exception as ex:
        logging.error(f'Unable to download JSON: {ex}', exc_info=True)


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
        resp = helper.fetch_form_data(payload="", headers=headers)
        if resp == 200:
            json_form_list = helper.read_form_list(all_form_list)
            # csv_form_list = helper.read_form_list(form_list_file)
            # fetch_csv_data(csv_form_list)
            fetch_json_data(json_form_list)

    else:
        logging.warning('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    logging.critical(f'Unable to read json file {err}', exc_info=True)
