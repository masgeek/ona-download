# Python program to
# demonstrate defining
# a class
import requests
import time
from contextlib import closing
import csv
from string import Template
from requests.exceptions import HTTPError
import json
from os import getenv, path
from dotenv import load_dotenv
import sqlite3
import shutil
from clint.textui import progress


def download_attachment(file_name, url, extension, page_no, form_name, save_dir):
    response = requests.get(url, stream=True)
    with open(f'{save_dir}/{file_name}.{extension}', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    

class OnaHelper:
    """
    @:param username
    @:param password
    @:param baseurl APi endpoint url
    """

    def __init__(self, username, password, my_logger, baseurl='https://api.ona.io', db_file='ona_form.db'):
        self.username = username
        self.password = password
        self.my_logger = my_logger
        self.baseurl = baseurl
        self.db_file = db_file

    def _auth_token(self):
        _url = self.baseurl + "/api/v1/user"
        _response = requests.get(_url, auth=(self.username, self.password))
        _response.raise_for_status()
        return _response.json()

    def _insert_to_database(self, json_data):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO ona_form_list values (?,?,?,?,?,?)', json_data)
            conn.commit()
            self.my_logger.debug(f'Inserted form {json_data[1]} with id {json_data[0]}')
        except sqlite3.IntegrityError as ie:
            self.my_logger.error('sqlite error: ', ie.args[0])  # column name is not unique
            conn.rollback()
        except Exception as e:
            self.my_logger.error(f'Unable to insert to table {e}')
            conn.rollback()
        c.close()

    def refresh_token(self, json_file):
        api_token = ""
        try:
            resp = self._auth_token()
            with open(json_file, 'w') as json_file_obj:
                json.dump(resp, json_file_obj, indent=4)
            api_token = resp['api_token']
        except HTTPError as http_err:
            self.my_logger.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            self.my_logger.error(f'Other error occurred: {err}')
        return api_token

    def fetch_form_data(self, payload, headers):
        self.my_logger.debug(f'----> Fetching form data')
        status_code = 0
        try:
            _url = self.baseurl + "/api/v1/data"
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()

            resp = _response.json()
            status_code = _response.status_code
            self.my_logger.debug(f'----> Finished fetching form data {_response.status_code}')
            for form in resp:
                form_data = [
                    form['id'],
                    form['id_string'],
                    form['title'],
                    form['description'],
                    form['url'],
                    time.time(),
                ]
                self._insert_to_database(form_data)
        except HTTPError as http_err:
            self.my_logger.error(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            self.my_logger.error(f'Other error occurred: {err}')

        return status_code

    def read_form_list(self, form_list_file):
        f = open(form_list_file, "r")
        file_string = f.read()
        file_list = file_string.replace('"', '').split(",")

        # Loop though the file list
        form_id_list = []
        form_id = 0
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for form_name in file_list:
            name = form_name.strip("\n").rstrip("\n")
            # Now we query the database
            c.execute('SELECT form_id,form_name FROM ona_form_list WHERE form_name = ?', (name,))
            data = [dict(row) for row in c.fetchall()]
            for form_data in data:
                form_id = form_data['form_id']
                form_name = form_data['form_name']
                form_id_list.append([form_id, form_name])
        f.close()
        conn.close()
        return form_id_list

    def download_json_form_data(self, form_id, payload, headers):
        _url = f'{self.baseurl}/api/v1/data/{form_id}'
        self.my_logger.debug(f'Running url {_url}')
        resp = json.loads("[]")
        try:
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()
            resp = _response.json()
        except HTTPError as http_err:
            self.my_logger.error(f'Unable to fetch form list: {http_err} form is {form_id}')
        except Exception as err:
            self.my_logger.error(f'Other error occurred: {err}')
        return resp

    def download_csv_form_data(self, form_id, payload, headers, file_name, download_format):
        _url = f'{self.baseurl}/api/v1/data/{form_id}.csv'
        self.my_logger.debug(f'Running {download_format} url {_url}')
        resp = 0
        try:
            _response = requests.get(_url, data=payload, headers=headers, stream=True)
            _response.raise_for_status()
            with open(file_name, "wb") as fileToSave:
                total_length = int(_response.headers.get('content-length'))
                expected_size = (total_length / 1024) + 1
                for chunk in progress.bar(_response.iter_content(chunk_size=1024), expected_size=expected_size):
                    if chunk:
                        fileToSave.write(chunk)
                        fileToSave.flush()

        except HTTPError as http_err:
            self.my_logger.error(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            self.my_logger.error(f'Other error occurred: {err}')
        return resp

    def download_form_attachments(self, form_id, payload, headers, page_no, page_size, media_type):
        _url = f'{self.baseurl}/api/v1/media?xform={form_id}&page={page_no}&page_size={page_size}&type={media_type}'
        self.my_logger.debug(f'Running attachment url {_url}')
        resp = json.loads("[]")
        try:
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()
            resp = _response.json()
        except HTTPError as http_err:
            self.my_logger.error(f'Unable to fetch form attachments: {http_err}')
        except Exception as err:
            self.my_logger.error(f'Other error occurred: {err}')
        return resp
