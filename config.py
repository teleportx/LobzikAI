from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ['DEBUG'] == 'TRUE'

db_url = environ['DB_URL']
amqp_url = environ['AMQP_URL']

openrouter_key = environ['OPENROUTER_KEY']
bot_token = environ['BOT_TOKEN']

db_pool_max_size = 5
