from os import getenv, path, walk
from dotenv import load_dotenv
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--user', '-u', help='Define user to download file', type=str, default='akilimo')
parser.add_argument('--password', '-p', help='FTP password', type=str)

args = parser.parse_args()

load_dotenv()

username = args.user
password = args.password
log_level = getenv('LOG_LEVEL', 'INFO')

for root, dirs, files in walk('downloads/converted'):
    for fName in files:
        fullFileName = path.join(root, fName)
        print(fullFileName)
