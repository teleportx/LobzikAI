import os
import requests
import zipfile
import io


def download_and_extract_zip(url: str, save_dir: str) -> None:
    os.makedirs(save_dir, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(save_dir)
