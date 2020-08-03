# Python program to
# demonstrate defining
# a class
import requests
import time
from requests.exceptions import HTTPError
import json
import sqlite3
import asyncio
from aiohttp import ClientSession


class OnaHelperMulti:
    """
    @:param username
    @:param password
    @:param baseurl APi endpoint url
    """

    def __init__(self, username, password, baseurl, db_file, form_list_file):
        self.username = username
        self.password = password
        self.baseurl = baseurl
        self.db_file = db_file
        self.form_list_file = form_list_file

    def _auth_token(self):
        _url = self.baseurl + "/api/v1/user"
        _response = requests.get(_url, auth=(self.username, self.password))
        _response.raise_for_status()
        return _response.json()

    async def _insert_to_database(self, json_data):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO ona_form_list values (?,?,?,?,?,?)', json_data)
            conn.commit()
            print(f'Inserted form {json_data[1]} with id {json_data[0]}')
        except sqlite3.IntegrityError as ie:
            print('sqlite error: ', ie.args[0])  # column name is not unique
            conn.rollback()
        except Exception as e:
            print(f'Unable to insert to table {e}')
            conn.rollback()
        c.close()

    async def refresh_token(self, json_file):
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

    async def fetch_form_data(self, payload, headers):
        print(f'----> Fetching form data')
        status_code = 0
        try:
            _url = self.baseurl + "/api/v1/data"
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()

            resp = _response.json()
            status_code = _response.status_code
            print(f'----> Finished fetching form data {_response.status_code}')
            for form in resp:
                form_data = [
                    form['id'],
                    form['id_string'],
                    form['title'],
                    form['description'],
                    form['url'],
                    time.time(),
                ]
                await self._insert_to_database(form_data)
        except HTTPError as http_err:
            print(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        return status_code

    async def read_form_list(self):
        f = open(self.form_list_file, "r")
        file_string = f.read()
        file_list = file_string.replace('"', '').split(",")

        # Loop though the file list
        form_id_List = []
        form_id = 0
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for form_name in file_list:
            name = form_name.strip("\n").rstrip("\n")
            # Now we query the database
            c.execute('SELECT form_id, form_name FROM ona_form_list WHERE form_name = ?', (name,))
            data = [dict(row) for row in c.fetchall()]
            for form_data in data:
                form_id = form_data['form_id']
                form_name = form_data['form_name']
                form_id_List.append([form_id, form_name])
        f.close()
        conn.close()
        return form_id_List

    async def download_json_form_data(self, form_id, payload, headers):
        _url = f'{self.baseurl}/api/v1/data/{form_id}'
        print(f'Running url {_url}')
        resp = json.loads("[]")
        try:
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()
            resp = _response.json()
        except HTTPError as http_err:
            print(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return resp

    async def download_csv_form_data(self, form_id, payload, headers):
        _url = f'{self.baseurl}/api/v1/data/{form_id}.csv'
        print(f'Running csv url {_url}')
        async with ClientSession() as session:
            async with session.get(_url, data=payload, headers=headers) as response:
                response = await response.text()
                return response

    async def download_csv_form_data_old(self, form_id, payload, headers):
        _url = f'{self.baseurl}/api/v1/data/{form_id}.csv'
        print(f'Running csv url {_url}')
        resp = 0
        try:
            _response = requests.get(_url, data=payload, headers=headers, stream=True)
            _response.raise_for_status()
            resp = _response.text
        except HTTPError as http_err:
            print(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return resp
