from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ['DEBUG'] == 'TRUE'
db_url = environ['DB_URL']

db_pool_max_size = 5
