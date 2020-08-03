import requests
from string import Template
from requests.exceptions import HTTPError
import json
import pandas as pd
import OnaHelper
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()

username = getenv('ONA_USERNAME')
password = getenv('ONA_PASSWORD')
tokenJsonFile = getenv('TOKEN_JSON')
db_file = 'ona_form.db'
form_list_file = 'formList.txt'
json_form_list_file = 'jsonFormList.txt'

rootUrl = "https://api.ona.io"

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
        print(f'Error reading {tokenJsonFile} file {fileErr}')
    # next sequence here
    if "api_token" in data:
        onaToken = data['api_token']
    else:
        print("No api token, requesting a new one")
        onaToken = helper.refresh_token(tokenJsonFile)
    if onaToken:
        headers = {'authorization': 'Token ' + onaToken}
        print(f'Found valid api token -> proceeding to fetch from metadata')
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
                    print(f'Pulling submission for {form_name}')
                    data_resp = helper.download_csv_form_data(form_id, payload="", headers=headers)

                    print(f'Reaponse is {data_resp}')
                    tagFile.write(data_resp)
                except Exception as err:
                    print(f'Unable to write CSV {form_name} for: {err}')
                finally:
                    tagFile.close()

    else:
        print('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    print(f'Unable to read json file generating a new one: {err}')
