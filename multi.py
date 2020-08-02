import requests
import pandas as pd
import concurrent.futures
import time
import json
import aiohttp
import asyncio
import OnaHelperMulti as Ona
from os import getenv
from dotenv import load_dotenv

load_dotenv()

username = getenv('ONA_USERNAME')
password = getenv('ONA_PASSWORD')
tokenJsonFile = getenv('TOKEN_JSON')
db_file = 'ona_form.db'
form_list_file = 'formList.txt'

rootUrl = "https://api.ona.io"

onaToken = ""
payload = ""
helper = Ona.OnaHelperMulti(username=username,
                            password=password,
                            baseurl=rootUrl,
                            db_file=db_file,
                            form_list_file=form_list_file)

data = json.loads("{}")


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, f'{rootUrl}/api/v1/users/mtariku')
        print(html)

# https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
