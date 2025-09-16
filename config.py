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
    num_asr_workers = int(environ.get('NUM_ASR_WORKERS', 8))
    chunk_overlapping = float(environ.get("CHUNK_OVERLAPPING", 2.0))


class AIModels:
    asr_model = environ.get("ASR_MODEL", "google/gemini-2.5-flash")
    sum_model = environ.get("SUMMARIZATION_MODEL", "openai/gpt-5-mini")
    mm_model = environ.get("MM_MODEL", "google/gemini-2.5-flash")
    local_asr_vosk_model = environ.get("LOCAL_ASR_VOSK_MODEL", "vosk-model-ru-0.22")
    test_maker_model = environ.get("TEST_MAKER_MODEL", "openai/gpt-4o-mini")
