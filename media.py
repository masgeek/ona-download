import json
import os
import logging
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
# logLevel = logging.DEBUG if CONFIG['log_debug_messages'] else logging.INFO
logfile = path.join(path.dirname(path.abspath(__file__)), "ona_media_download.log")
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    handlers=[logging.FileHandler(logfile, 'w', 'utf-8')],
                    level=log_level)

onaToken = ""
payload = ""
helper = OnaHelper.OnaHelper(username='mtariku', password='applenose', my_logger=logging)

logging.debug(f'Using the following credentials username: {username}')

data = json.loads("{}")


def fetch_media_files(form_id, form_name, page_number):
    try:
        logging.info(f'Pulling attachments for {form_id}')
        data_resp = helper.download_form_attachments(form_id, payload="", headers=headers,
                                                     page_no=page_number, page_size=50, media_type="image")

        base_path = f'downloads/images/{form_name}'
        if not os.path.exists(base_path):
            logging.info(f'This base path {base_path} does not exist creating it')
            os.mkdir(base_path)

        for form in data_resp:
            save_dir = f'{base_path}/page_{page_number}'
            if not os.path.exists(save_dir):
                logging.info(f'This path {save_dir} does not exist for {form_name}')
                os.mkdir(save_dir)
            file_name = form["id"]
            attachment_url = form["download_url"]
            filename = form["filename"]
            _downloadData = filename.split('.')
            extension = _downloadData[1]

            # logging.info(f'Filename is {filename} and extension is {extension}-------->')
            logging.info(f'Downloading attachment is {attachment_url} and extension is {extension}-------->')
            helper.download_attachment(file_name=file_name, url=attachment_url,
                                       extension=extension, page_no=page_number,
                                       form_name=form_name, save_dir=save_dir)

    except Exception as ex:
        logging.error(f'Unable to download attachments: {ex}', exc_info=True)


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
        # Loop through certain range to denote number of pages
        for x in range(1, 501, 1):
            logging.info(f'Fetching data in Page number {x}')
            fetch_media_files(form_id="337918", form_name="Score_Weed_Control_AC", page_number=x)
    else:
        logging.warning('Unable to fetch token, please check your connection -> Exiting now, sorry human')

except FileNotFoundError as err:
    logging.critical(f'Unable to read json file {err}', exc_info=True)
