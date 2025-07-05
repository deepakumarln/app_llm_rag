import re
from typing import Any, AsyncGenerator

import aiofiles

import asyncio
import spacy
from spacy.language import Language
import tiktoken as tk
import time
from httpx import AsyncClient
from http import HTTPStatus
import httpx
from starlette.concurrency import run_in_threadpool
from loguru import logger
from .exceptions import EmbedMaxConnectionTimeout, EmbedMethodException
import inspect

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50

async def load(filepath: str) -> AsyncGenerator[str, Any]:
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f: 
        while chunk := await f.read(DEFAULT_CHUNK_SIZE):
            yield chunk

def clean(text: str) -> str:
    logger.debug('inside the clean block')
    t = text.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\. ,", "", t)
    t = t.replace("..", ".")
    t = t.replace(". .", ".")
    cleaned_text = t.replace("\n", " ").strip()
    return cleaned_text 

def count_tokens(string: str, encoding_name="cl100k_base") -> int:
    # Get the encoding
    encoding = tk.get_encoding(encoding_name)
    
    # Encode the string
    encoded_string = encoding.encode(string, disallowed_special=())

    # Count the number of tokens
    num_tokens = len(encoded_string)
    return num_tokens


def split_sentences_by_spacy(text:str, max_tokens:int, models:dict, overlap:int=0) -> list[str]:
    
    logger.debug(f'inside the split sentences by spacy block')
    # Load spaCy model
    try:
        nlp = models['spacy']
    except Exception as e:
        raise Exception(e)
    
    #nlp = spacy.load('./en_core_web_sm/en_core_web_sm/en_core_web_sm-3.8.0/',disable=['tagger','ner','lemmatizer','textcat'])
        
    doc = nlp(text)#,disable=['tagger','ner','lemmatizer','textcat'])
    
    sentences = [sent.text for sent in doc.sents]
    #print(sentences[:10])
    # Tokenize sentences into tokens and accumulate tokens
    tokens_lengths = [count_tokens(sent) for sent in sentences]
    
    chunks = []
    start_idx = 0
    
    
    while start_idx < len(sentences):
        current_chunk = []
        current_token_count = 0
        for idx in range(start_idx, len(sentences)):
            if current_token_count + tokens_lengths[idx] > max_tokens:
                break
            current_chunk.append(sentences[idx])
            current_token_count += tokens_lengths[idx]
        
        chunks.append(" ".join(current_chunk))
        
        # Sliding window adjustment
        if overlap >= len(current_chunk):
            start_idx += 1
        else:
            start_idx += len(current_chunk) - overlap

    return chunks

async def get_text_chunks(file_name:str,models:dict) -> list[str]:
    logger.debug(f'inside of get_text_chunks for file -> {file_name}')
    async for chunks in load(file_name):
        logger.debug(f'inside of get_text_chunks, processing chunk')
        if not chunks:
            return
        cleaned = await run_in_threadpool(clean,chunks)
        t0 = time.perf_counter()
        spacy_chunks = await run_in_threadpool(split_sentences_by_spacy,cleaned,512,models,0)
        logger.debug(f'finished processing get_text_chunks for file -> {file_name}, and the time it took is {time.perf_counter() - t0:.4f}')
    return spacy_chunks

async def embed(text: str,url:str,semaphore:asyncio.Semaphore=None) -> list[float]:
    #logger.debug(f'getting embedding for text -> {text}')
    async with semaphore:
        try:
            async with AsyncClient() as client:
                response = await client.post(url=url,json={'text':text})
                #logger.debug(f'got response for text -> {text} status_code -> {response.status_code}')
                if semaphore.locked():
                    logger.debug(f"Concurrency limit reached for function -> {inspect.stack()[1][3]}, waiting for 60 Seconds")
                    await asyncio.sleep(60)
                if response.status_code == HTTPStatus.OK:
                    #logger.debug(f'returing the embeddings to')
                    return text, response.json()['embeddings'] 
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    await asyncio.sleep(int(response.json()['retry_after_seconds']))
                    raise EmbedMaxConnectionTimeout(text=text)
        except httpx.ConnectTimeout as connect_timeout:
            raise EmbedMethodException('Connection Timed Out',text=text)
        except Exception as e:
            raise EmbedMethodException(str(e),text=text)
    
    