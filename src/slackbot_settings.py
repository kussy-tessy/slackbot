import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(load_dotenv)

API_TOKEN = os.environ.get('TOKEN')

PLUGINS=[
    'my_plugins',
]