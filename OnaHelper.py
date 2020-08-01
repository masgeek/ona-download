# Python program to
# demonstrate defining
# a class
import requests
from string import Template
from requests.exceptions import HTTPError
import json
from os import getenv, path
from dotenv import load_dotenv
import sqlite3


class OnaHelper:
    """@:param username"""
    """@:param password"""
    """@:param baseurl APi endpoint url"""

    def __init__(self, username, password, baseurl):
        self.username = username
        self.password = password
        self.baseurl = baseurl
        self.conn = sqlite3.connect('ona_form.db')

    def _auth_token(self):
        _url = self.baseurl + "/api/v1/user"
        _response = requests.get(_url, auth=(self.username, self.password))
        _response.raise_for_status()
        return _response.json()

    def _create_database(self):
        c = self.conn.cursor()

    def refresh_token(self, json_file):
        api_token = ""
        try:
            resp = self._auth_token()
            with open(json_file, 'w') as json_file_obj:
                json.dump(resp, json_file_obj, indent=4)
            api_token = resp['api_token']
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return api_token

    def fetch_form_data(self, payload, headers):
        print(f'----> Fetching form data')
        _url = self.baseurl + "/api/v1/data"
        _response = requests.get(_url, data=payload, headers=headers)
        _response.raise_for_status()

        resp = _response.json()
        for form in resp:
            print('----------------')
            print(form)
            print('----------------')

        print(f'----> Finished fetching form data {_response.status_code}')
        return ""
