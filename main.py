import requests
from string import Template
from requests.exceptions import HTTPError
import json
import OnaHelper
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()

username = getenv('ONA_USERNAME')
password = getenv('ONA_PASSWORD')
tokenJsonFile = getenv('TOKEN_JSON')
db_file = 'ona_form.db'

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
        helper.fetch_form_data(payload="", headers=headers)
    else:
        print('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    print(f'Unable to read json file generating a new one: {err}')
