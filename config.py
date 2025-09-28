from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ['DEBUG'] == 'TRUE'
host = environ['HOST']

db_url = environ['DB_URL']
amqp_url = environ['AMQP_URL']

openrouter_key = environ['OPENROUTER_KEY']
bot_token = environ['BOT_TOKEN']
jwt_secret = environ['JWT_SECRET']

telegram_bot_api_server = environ.get('TELEGRAM_BOT_API_SERVER')
model_cache_dir = environ.get("MODEL_CACHE_DIR", "./cache")

use_local_asr = environ.get('USE_LOCAL_ASR', "TRUE") == "TRUE"


class Constants:
    db_pool_max_size = 5
    num_asr_workers = int(environ.get('NUM_ASR_WORKERS', 8))
    chunk_overlapping = float(environ.get("CHUNK_OVERLAPPING", 2.0))
    remote_asr_chunk_size_mb = 4

    lecture_token_ttl = 365 * 24 * 60 * 60


class AIModels:
    asr_model = environ.get("ASR_MODEL", "google/gemini-2.5-flash")
    sum_model = environ.get("SUMMARIZATION_MODEL", "openai/gpt-5-mini")
    mm_model = environ.get("MM_MODEL", "google/gemini-2.5-flash")
    local_asr_vosk_model = environ.get("LOCAL_ASR_VOSK_MODEL", "vosk-model-ru-0.22")
    base_gpt_model = environ.get("BASE_GPT_MODEL", "openai/gpt-4o-mini")
