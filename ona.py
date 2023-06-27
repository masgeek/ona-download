import concurrent.futures
import json
import sqlite3
from os import getenv

import typer
from rich.progress import track

from my_logger import MyLogger

# noinspection PyPackageRequirements
from dotenv import load_dotenv
from ona.OnaHelper import OnaHelper
from processing.ProcessData import ProcessData, ProcessDb
from db.models import create_tables, OnaForms

load_dotenv()

app = typer.Typer()

logger = MyLogger()
ona_helper = OnaHelper()

db_file = 'db/ona_form.db'
ona_process = ProcessData(db_file=db_file)
ona_db = ProcessDb(db_file=db_file)

default_user = getenv('ONA_USER', 'touma')
default_pass = getenv('ONA_PASSWORD', 'andalite6')
token_file = f'tokens/ona.json'


@app.command(name="init")
def init_db():
    create_tables()


@app.command(name="auth")
def main():
    """
    Authenticate an ONA user and set the access token
    """
    username = typer.prompt("Enter ONA username or press enter to use default", default=default_user,
                            show_default=True)
    password = typer.prompt("Enter ONA password or press enter to use default", default=default_pass, show_default=True,
                            hide_input=True)

    logger.debug(f"Welcome {username.upper()}")

    refresh = typer.confirm("Refresh access token?", default=True)
    if refresh:
        logger.info(f"Refreshing access token -->")
        access_token = ona_helper.refresh_token(json_file=token_file, username=username, password=password)
    else:
        access_token = ona_process.read_token_file(token_file=token_file)
        logger.info("Skipping token refreshing and reading saved one in file")
    logger.debug(f"Refreshed token is -> {access_token}")


@app.command(name="forms")
def fetch_form():
    """
    Fetch a list of forms from ona
    """
    access_token = ona_process.read_token_file(token_file=token_file)
    headers = {'authorization': 'Token ' + access_token}
    form_list = ona_helper.fetch_form_list(payload=None, headers=headers)
    OnaForms.insert_many(form_list).execute()


@app.command(name="data")
def download_data():
    """
    Download data from list of forms
    """
    access_token = ona_process.read_token_file(token_file=token_file)
    headers = {'authorization': 'Token ' + access_token}
    form_list = ona_process.read_all_forms()
    if len(form_list) <= 0:
        logger.info("No forms to process")
    else:
        # ona_process.fetch_json_data(form_id_list=form_list, headers=headers, json_path='json_ona_data/trial')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            logger.info("Processing forms")
            for form in form_list:
                logger.info(f"form data is {form}")
                _result = executor.submit(ona_helper.fetch_form_data, form[0], headers)
                _result.add_done_callback(ona_process.process_form_data)


if __name__ == "__main__":
    app()
