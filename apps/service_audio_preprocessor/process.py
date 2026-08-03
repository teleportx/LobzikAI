import asyncio
import uuid
from pathlib import Path

import aioboto3
from aiofiles import tempfile
from aiogram import Bot
from loguru import logger

from libs import config
from libs.utils.get_bot_api_session import get_bot_api_session

sample_rate = 16000
codec = "pcm_s16le"

bot = Bot(config.bot_token, session=get_bot_api_session(config.telegram_bot_api_server))
s3_session = aioboto3.Session(config.S3.access_key, config.S3.secret_key)


def build_filter_complex(n: int) -> str:
    """CHUDO AHHAHA"""

    parts = []
    labels = []
    for i in range(n):
        parts.append(
            f'[{i}:a]aformat=sample_rates={sample_rate}:channel_layouts=mono[a{i}]'
        )
        labels.append(f"[a{i}]")
    concat_part = f'{''.join(labels)}concat=n={n}:v=0:a=1[out]'
    return ';'.join(parts) + ';' + concat_part


async def upload_to_s3(
        data: bytes,
        content_type: str,
) -> str:

    full_key = f'asr/{uuid.uuid4()}.wav'

    async with s3_session.client('s3', use_ssl=config.S3.use_ssl, endpoint_url=config.S3.endpoint) as s3:
        await s3.put_object(
            Bucket=config.S3.bucket,
            Key=full_key,
            Body=data,
            ContentType=content_type,
        )
        url = await s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.S3.bucket, 'Key': full_key},
            ExpiresIn=60 * 60 * 24,
        )

    logger.debug("Uploaded %d bytes -> s3://%s/%s", len(data), config.S3.bucket, full_key)
    return url


async def process_files(file_ids: list[str]) -> str:
    infile_names = [uuid.uuid4() for _ in file_ids]
    logger.debug(f'Start processing {file_ids}')

    cmd = ['ffmpeg']
    filter_complex = build_filter_complex(len(file_ids))

    async with tempfile.TemporaryDirectory() as tmpdir:
        async with asyncio.TaskGroup() as tg:
            for i, file_id in enumerate(file_ids):
                file_info = await bot.get_file(file_id)
                timeout = (file_info.file_size // 1024 ** 2) * 2
                tg.create_task(
                    bot.download(file_id, Path(tmpdir) / str(infile_names[i]), timeout=timeout)
                )

        logger.debug(f'Downloaded {file_ids}')

        for el in infile_names:
            cmd += ["-i", str(Path(tmpdir) / str(el))]

        cmd += [
            '-filter_complex', filter_complex,
            '-map', "[out]",
            '-ac', '1',
            '-ar', str(sample_rate),
            '-c:a', codec,
            '-f', 'wav',
            '-',
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f'Error while working with ffmpeg: {stderr.decode()}')

    return await upload_to_s3(stdout, 'audio/wav')
