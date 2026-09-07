from os import environ
from dotenv import load_dotenv

load_dotenv()

debug = environ["DEBUG"] == "TRUE"
host = environ["HOST"]

db_url = environ["DB_URL"]
amqp_url = environ["AMQP_URL"]

bot_token = environ["BOT_TOKEN"]
jwt_secret = environ["JWT_SECRET"]

telegram_bot_api_server = environ.get("TELEGRAM_BOT_API_SERVER")
model_cache_dir = environ.get("MODEL_CACHE_DIR", "./cache")


class ASRSettings:
    batch_size = int(environ.get("ASR_BATCH_SIZE", 4))
    device = environ.get("ASR_DEVICE", "cuda")
    model = environ.get("ASR_MODEL", "bzikst/faster-whisper-large-v3-russian-int8")
    compute_dtype = environ.get("ASR_COMPUTE_DTYPE", "int8_float16")


class Constants:
    db_pool_max_size = 5
    lecture_token_ttl = 365 * 24 * 60 * 60


class AIModels:
    sum_model = environ.get("SUMMARIZATION_MODEL", "gpt-5-mini")
    base_gpt_model = environ.get("BASE_GPT_MODEL", "gpt-5-nano")


class S3:
    endpoint = environ["S3_ENDPOINT"]
    bucket = environ["S3_BUCKET"]
    use_ssl = environ.get("S3_SSL") != "FALSE"
    access_key = environ["S3_ACCESS_KEY"]
    secret_key = environ["S3_SECRET_KEY"]
