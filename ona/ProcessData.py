import concurrent.futures
import json
import pathlib

from my_logger import MyLogger
from ona.OnaHelper import OnaHelper


class ProcessData:
    def __init__(self):
        self.logger = MyLogger()
        self.helper = OnaHelper()

    def read_token_file(self, token_file):
        try:
            with open(token_file) as json_file_obj:
                data = json.load(json_file_obj)
                if "api_token" in data:
                    return data['api_token']
        except Exception as fileErr:
            self.logger.error(f'Error reading {token_file} file {fileErr}')

        return None

    def fetch_json_data(self, form_id_list, headers, json_path='json_ona_data', sub_dir=''):
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for form in form_id_list:
                    form_id = form[0]
                    form_name = form[1]
                    save_path = f'{json_path}/{sub_dir}'
                    self.check_dir(save_path)
                    json_file = f'{save_path}/{form_name}.json'
                    executor.submit(self.save_json_file, form_id, form_name, json_file, headers)
        except Exception as ex:
            self.logger.error(f'Unable to download JSON: {ex}', exc_info=True)

    def save_json_file(self, form_id, form_name, json_file, headers):
        try:
            self.logger.info(f'Pulling submission for -> {form_name}')
            data_resp = self.helper.download_json_form_data(form_id, headers=headers)
            if len(data_resp) > 0:
                with open(json_file, 'w') as json_file_wr:
                    json.dump(data_resp, json_file_wr, indent=4)
                    self.logger.info(f'Form {form_name} has been saved with {len(data_resp)} submissions')
                    self.logger.debug(f'File saved {json_file}')
            else:
                self.logger.error(f'Unable to save file: {json_file}')
        except Exception as errEx:
            self.logger.error(f'Unable to write JSON {form_name} for: {errEx}', exc_info=True)

    def check_dir(self, save_path):
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
        self.logger.debug(f'The new directory {save_path} has been created!')
