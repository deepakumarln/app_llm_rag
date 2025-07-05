#import sys
#sys.path.append('.')
import os

from loguru import logger
from .repository import ElasticRepository
from .transform import get_text_chunks, embed,clean
from datetime import datetime
from asyncio import Semaphore
import asyncio
from .exceptions import EmbedMaxConnectionTimeout, EmbedMethodException
#from ..models.schema import EmbeddingData
from fastapi import BackgroundTasks

EMBEDDING_MAX_REQ = 5

class VectorService(ElasticRepository): 
    #EMBEDDING_SEMAPHORE = Semaphore(EMBEDDING_MAX_REQ)
    def __init__(self):
        super().__init__()
        
    async def store_file_content_in_db(self,
        file_path: str,
        url:str,
        models:dict,
        store_semaphore:Semaphore,
        index_name: str = "search_index",
    ) -> None:
        logger.debug(f'inside store file content in db block...')
        if os.path.getsize(filename=file_path) == 0:
            logger.debug(f'file -> {file_path} is a 0 size file')
            return
        chunks = await get_text_chunks(file_name=file_path,models=models)
        logger.debug(f'the size of chunks is {len(chunks)}')
        #embed_semaphore = Semaphore(EMBEDDING_MAX_REQ)
        time_stamp = datetime.now()
        file_name = os.path.basename(file_path)
        tasks = [embed(chunk,url,store_semaphore) for chunk in chunks]
        tasks_to_run = asyncio.as_completed(tasks)
        for task in tasks_to_run:
            try:
                chunk, embeddings = await task
                logger.debug(f'store file in db semaphore -> {store_semaphore}')
                logger.debug(f'starting insert into elastic database')
                await self.insert(
                    index_name=index_name, data={"file_name":file_name,"time_stamp":str(time_stamp),
                                                "doc_text":chunk,"embeddings":embeddings}
                )
            except EmbedMaxConnectionTimeout as embed_exception_timeout:
                text = embed_exception_timeout.text
                logger.debug(f'Got exception -> {exception_message} for text -> {text}')
            except EmbedMethodException as embed_exception:
                exception_message = embed_exception.exception_message
                text = embed_exception.text
                logger.debug(f'Got exception -> {exception_message} for text -> {text}')
            
    async def get_content_from_db(self,text:str,url:str,search_semaphore:asyncio.Semaphore)->list[str]:
        logger.debug(f'inside get contenct from db for -> {text}')
        logger.debug(f'get file from db semaphore -> {search_semaphore}')
        _, embeddings = await embed(clean(text),url,search_semaphore)
        #print('embeddings for search ',embeddings)
        texts = []
        async for text in self.search(index_name='search_index',text=text,embeddings=embeddings):
            texts.append(text)
        logger.debug(f'got texts -> {texts}')
        content = '\n'.join([i['text'] for i in texts])
        logger.debug(f'the contect is -> {content}')
        return content
    
vector_service = VectorService()
