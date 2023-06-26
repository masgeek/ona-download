import concurrent.futures
import json
import pathlib
import sqlite3
import string

from my_logger import MyLogger


class ProcessData:
    def __init__(self, db_file='ona_form.db'):
        self.logger = MyLogger()
        self.db_file = db_file

    def read_token_file(self, token_file):
        try:
            with open(token_file) as json_file_obj:
                data = json.load(json_file_obj)
                if "api_token" in data:
                    return data['api_token']
        except Exception as fileErr:
            self.logger.error(f'Error reading {token_file} file {fileErr}')

        return None

    def insert_to_database(self, json_data):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO ona_form_list values (?,?,?,?,?,?)', json_data)
            conn.commit()
            self.logger.debug(f'Inserted form {json_data[1]} with id {json_data[0]}')
        except sqlite3.IntegrityError as ie:
            self.logger.error('SQlite error: ', ie.args[0])  # column name is not unique
            conn.rollback()
        except Exception as e:
            self.logger.error(f'Unable to insert to table {e}')
            conn.rollback()

        c.close()

    def read_all_forms(self) -> list[list[string]]:
        form_id_list: list[list[string]] = []
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Now we query the database
        c.execute('SELECT form_id,form_name FROM ona_form_list')
        data = [dict(row) for row in c.fetchall()]
        for form_data in data:
            form_id = form_data['form_id']
            form_name = form_data['form_name']
            form_id_list.append([form_id, form_name])
            self.logger.info(f'Processing form name `{form_name}` -> `{form_id}`')

        conn.close()

        return form_id_list

    def read_form_list(self, form_list_file: string) -> list[list[string]]:
        f = open(form_list_file, "r")
        file_string = f.read()
        file_list = file_string.replace('"', '').split(",")

        # Loop though the file list
        form_id_list: list[list[string]] = []
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
                self.logger.info(f'Processing form name `{form_name}` -> `{form_id}`')
        f.close()
        conn.close()
        return form_id_list

    def fetch_json_data(self, form_id_list, headers, json_path='json_ona_data', sub_dir=''):
        try:
            save_path = f'{json_path}/{sub_dir}'
            self.check_dir(save_path)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for form in form_id_list:
                    form_id = form[0]
                    form_name = form[1]
                    json_file = f'{save_path}/{form_name}.json'
                    executor.submit(self.save_json_file, form_id, form_name, json_file, headers)
        except Exception as ex:
            self.logger.error(f'Unable to download JSON: {ex}')

    def save_json_file(self, form_id, form_name, json_file, headers):
        try:
            self.logger.info(f'Pulling submission for -> {form_name}')
            data_resp = []  # self.helper.download_json_form_data(form_id, headers=headers)
            stats = helper.fetch_form_stats(form_id, headers=headers)

            self.logger.info(f'Form stats is {stats}')
            if len(data_resp) > 0:
                with open(json_file, 'w') as json_file_wr:
                    json.dump(data_resp, json_file_wr, indent=4)
                    self.logger.info(f'Form {form_name} has been saved with {len(data_resp)} submissions')
                    self.logger.debug(f'File saved {json_file}')
            else:
                self.logger.error(f'Unable to save file --> {json_file}')
        except Exception as errEx:
            self.logger.error(f'Unable to write JSON {form_name} for: {errEx}', exc_info=True)

    def check_dir(self, save_path):
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
        self.logger.debug(f'The new directory {save_path} has been created!')
