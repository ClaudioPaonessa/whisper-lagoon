import os
import tarfile
from pathlib import Path

import requests

download_paths = {
    "small": {
        "int8": os.getenv("SMALL_INT8"),
        "float16": os.getenv("SMALL_FLOAT16"),
    },
    "medium": {
        "int8": os.getenv("MEDIUM_INT8"),
        "float16": os.getenv("MEDIUM_FLOAT16"),
    },
    "large-v2": {
        "int8": os.getenv("LARGE_INT8"),
        "float16": os.getenv("LARGE_FLOAT16"),
    },
}


def _download_file(url: str, destination: Path):
    print(f"Downloading {url} to {destination}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination, "wb") as f:
            total_downloaded = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    total_downloaded += len(chunk)
                    if total_downloaded >= 10485760:  # 10 MB
                        print(".", end="", flush=True)
                        total_downloaded = 0
        print("\nDownload complete.")
    else:
        print(f"Download failed with status code {response.status_code}")


def _download_model(
    model_data_dir: str, whisper_model_name: str, quantization: str
) -> None:
    model_folder = Path(model_data_dir, f"{whisper_model_name}_{quantization}")

    model_folder.mkdir(parents=True, exist_ok=True)

    download_path = Path(model_data_dir, f"{whisper_model_name}_{quantization}.tar")
    _download_file(
        download_paths[whisper_model_name][quantization],
        download_path,
    )

    with tarfile.open(download_path, "r") as tar_file:
        tar_file.extractall(model_folder)

    # delete downloaded file after extraction
    os.remove(download_path)


def download_model_if_not_cached(
    model_data_dir: str, whisper_model_name: str, quantization: str
) -> Path:
    model_folder = Path(model_data_dir, f"{whisper_model_name}_{quantization}")

    # config.json, model.bin, tokenizer.json, vocabulary.json
    if Path(model_folder, "model.bin").exists():
        return model_folder

    _download_model(model_data_dir, whisper_model_name, quantization)

    return model_folder
