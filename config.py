from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ['DEBUG'] == 'TRUE'
db_url = environ['DB_URL']

bot_token = environ['BOT_TOKEN']

db_pool_max_size = 5
