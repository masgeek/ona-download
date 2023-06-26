# Python program to
# demonstrate defining
# a class
import json
import shutil
import string
import time

import requests
from clint.textui import progress
from requests.exceptions import HTTPError
from processing.ProcessData import ProcessData

from my_logger import MyLogger


def download_attachment(file_name, url, extension, page_no, form_name, save_dir):
    response = requests.get(url, stream=True)
    with open(f'{save_dir}/{file_name}.{extension}', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


class OnaHelper:
    """
    @:param baseurl APi endpoint url
    """

    def __init__(self, baseurl='https://api.ona.io'):
        self.logger = MyLogger()
        self.ona_process = ProcessData()
        self.baseurl = baseurl

    def _auth_token(self, username, password):
        _url = self.baseurl + "/api/v1/user"
        _response = requests.get(_url, auth=(username, password))
        _response.raise_for_status()
        return _response.json()

    def refresh_token(self, json_file, username, password):
        api_token = ""
        try:
            resp = self._auth_token(username, password)
            with open(json_file, 'w') as json_file_obj:
                json.dump(resp, json_file_obj, indent=4)
            api_token = resp['api_token']
        except HTTPError as http_err:
            self.logger.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')
        return api_token

    def fetch_form_data(self, payload, headers):
        self.logger.debug(f'----> Fetching form data')
        status_code = 0
        try:
            _url = self.baseurl + "/api/v1/data"
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()

            resp = _response.json()
            status_code = _response.status_code
            self.logger.debug(f'----> Finished fetching form data {_response.status_code}')
            for form in resp:
                form_data = [
                    form['id'],
                    form['id_string'],
                    form['title'],
                    form['description'],
                    form['url'],
                    time.time(),
                ]
                self.ona_process.insert_to_database(form_data)
        except HTTPError as http_err:
            self.logger.error(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')

        return status_code

    def fetch_form_stats(self, form_id: string, headers: list, group_by: string = '_xform_id') -> int:
        _url = f'{self.baseurl}/api/v1/stats/submissions/{form_id}?group={group_by}&name=total_records'
        total_records: int = 0
        try:
            _response = requests.get(_url, headers=headers)
            _response.raise_for_status()
            self.logger.debug(_response.json())
            resp = _response.json()
            total_records = resp[0]['count']
        except HTTPError as http_err:
            self.logger.error(f'Unable to fetch form list: {http_err} form is {form_id}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')

        return total_records

    def download_json_form_data(self, form_id, payload=None, headers=None):
        sort = '{"_submission_time":-1}'
        _url = f'{self.baseurl}/api/v1/data/{form_id}?sort={sort}&page=1&page_size=200'
        self.logger.debug(f'Running url {_url}')
        resp = json.loads("[]")
        try:
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()
            resp = _response.json()

            self.logger.debug("Header information is ->")
            self.logger.debug(_response.headers.get('link'))
        except HTTPError as http_err:
            self.logger.error(f'Unable to fetch form list: {http_err} form is {form_id}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')
        return resp

    def download_csv_form_data(self, form_id, payload, headers, file_name, download_format):
        _url = f'{self.baseurl}/api/v1/data/{form_id}.csv'
        self.logger.debug(f'Running {download_format} url {_url}')
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
            self.logger.error(f'Unable to fetch form list: {http_err}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')
        return resp

    def download_form_attachments(self, form_id, payload, headers, page_no, page_size, media_type):
        _url = f'{self.baseurl}/api/v1/media?xform={form_id}&page={page_no}&page_size={page_size}&type={media_type}'
        self.logger.debug(f'Running attachment url {_url}')
        resp = json.loads("[]")
        try:
            _response = requests.get(_url, data=payload, headers=headers)
            _response.raise_for_status()
            resp = _response.json()
        except HTTPError as http_err:
            self.logger.error(f'Unable to fetch form attachments: {http_err}')
        except Exception as err:
            self.logger.error(f'Other error occurred: {err}')
        return resp
