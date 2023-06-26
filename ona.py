import json
import string
from os import getenv

import typer
import time
from rich import print
from typing_extensions import Annotated
from rich.progress import track
from my_logger import MyLogger

# noinspection PyPackageRequirements
from dotenv import load_dotenv
from ona.OnaHelper import OnaHelper
from ona.ProcessData import ProcessData

load_dotenv()

app = typer.Typer()

logging = MyLogger()
ona_helper = OnaHelper()
ona_process = ProcessData()

default_user = getenv('ONA_USER', 'touma')
default_pass = getenv('ONA_PASSWORD', 'andalite6')


@app.command(name="start")
def main():
    """
    Authenticate an ONA user and set the access token
    """
    username = typer.prompt("Enter ONA username or press enter to use default", default=default_user,
                            show_default=False)
    password = typer.prompt("Enter ONA password or press enter to use default", default=default_pass, show_default=True)

    logging.debug(f"Welcome {username.upper()}")

    token_file = f'tokens/{username}.json'
    delete = typer.confirm("Refresh access token?")
    if delete:
        logging.info(f"Refreshing access token -->")
        access_token = ona_helper.refresh_token(json_file=token_file)
    else:
        access_token = ona_process.read_token_file(token_file=token_file)
    logging.debug(f"Refreshed token is -> {access_token}")


@app.command(name="fetch")
def fetch_form():
    """
    Fetch a list of forms from ona
    """
    username = typer.prompt("Enter ONA username or press enter to use default", default=default_user,
                            show_default=False)

    token_file = f'tokens/{username}.json'
    access_token = ona_process.read_token_file(token_file=token_file)
    headers = {'authorization': 'Token ' + access_token}

    form_data = ona_helper.fetch_form_data(payload=None, headers=headers)


@app.command(name="download")
def download_data():
    """
    Download data from list of specified forms
    """
    username = typer.prompt("Enter ONA username or press enter to use default", default=default_user,
                            show_default=True)
    all_form_list = typer.prompt("Enter file with list of form names", default="jsonFormList.txt", show_default=True)

    token_file = f'tokens/{username}.json'
    access_token = ona_process.read_token_file(token_file=token_file)
    headers = {'authorization': 'Token ' + access_token}
    json_form_list = ona_helper.read_all_forms()
    ona_process.fetch_json_data(form_id_list=json_form_list, headers=headers, json_path='json_ona_data/trial')


if __name__ == "__main__":
    app()
