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

rootUrl = "https://api.ona.io"

onaToken = ""
payload = ""
headers = {'authorization': 'Token ' + onaToken}
helper = OnaHelper.OnaHelper(username=username, password=password, baseurl=rootUrl)

print(f'Using the following credentials username: {username} and password: {password}')

try:
    with open(tokenJsonFile) as json_file_obj:
        data = json.load(json_file_obj)
        if "api_token" in data:
            onaToken = data['api_token']
            print(f'Found api token: {onaToken} -> proceeding to fetch from metadata')
        else:
            print("No api token, requesting a new one")
            onaToken = helper.refresh_token(tokenJsonFile)
    if not onaToken:
        helper.fetch_form_data(onaToken)
    else:
        print('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    print(f'Unable to read json file generating a new one: {err}')
