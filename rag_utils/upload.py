import os
import aiofiles
from aiofiles.os import makedirs
from fastapi import UploadFile
from loguru import logger

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 megabytes

async def save_upload_file(file: UploadFile) -> str:
    '''save file in the dir'''
    await makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)
    logger.debug(f'uploading file -> {file.filename} to path {filepath}')
    async with aiofiles.open(filepath, "wb") as f:
        while chunk := await file.read(DEFAULT_CHUNK_SIZE):
            await f.write(chunk)
    logger.debug(f'uploading file -> {file.filename} to path {filepath} completed!')
    return filepath
