from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ['DEBUG'] == 'TRUE'
host = environ['HOST']

db_url = environ['DB_URL']
amqp_url = environ['AMQP_URL']

openrouter_key = environ['OPENROUTER_KEY']
bot_token = environ['BOT_TOKEN']

telegram_bot_api_server = environ.get('TELEGRAM_BOT_API_SERVER')
model_cache_dir = environ.get("MODEL_CACHE_DIR", "./cache")


class Constants:
    db_pool_max_size = 5
    num_asr_workers = 8


class AIModels:
    asr_model = environ.get("ASR_MODEL", "google/gemini-2.5-flash")
    sum_model = environ.get("SUMMARIZATION_MODEL", "openai/gpt-5-mini")
    mm_model = environ.get("MM_MODEL", "google/gemini-2.5-flash")
    local_asr_vosk_model = environ.get("LOCAL_ASR_VOSK_MODEL", "vosk-model-ru-0.22")

