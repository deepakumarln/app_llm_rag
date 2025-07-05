from fastapi import FastAPI, HTTPException, status, File, BackgroundTasks, Body, Depends, Request, Response
from typing import Annotated, AsyncIterator
from rag_utils.upload import save_file
from fastapi import UploadFile
from rag_utils.service import vector_service, EMBEDDING_MAX_REQ
from rag_utils.extractor import extract_pdf
from rag_utils.dependencies import get_rag_text
from loguru import logger
from models.schema import RAGRequest,RAGSearchUtils
import httpx
import json
import re
from typing import Callable, Awaitable
from uuid import uuid4
import time
from datetime import datetime,timezone
from contextlib import asynccontextmanager
import spacy
from asyncio import PriorityQueue
import asyncio
from openai import AsyncOpenAI

models = {}

embedding_queue = PriorityQueue(maxsize=EMBEDDING_MAX_REQ)

embed_semaphore_store = asyncio.Semaphore(EMBEDDING_MAX_REQ)
embed_semaphore_search = asyncio.Semaphore(EMBEDDING_MAX_REQ)

OPENAI_KEY = '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'

EMBED_URL = 'http://jinai:7788/embed'

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_KEY,
)

def rag_search_utils():
    return {'semaphore':embed_semaphore_search,'embed_url':EMBED_URL}


@asynccontextmanager
async def load_models(_:FastAPI) -> AsyncIterator[None]:
    models['spacy'] = spacy.load('./en_core_web_sm/en_core_web_sm/en_core_web_sm-3.8.0/',disable=['tagger','ner','lemmatizer','textcat'])
    logger.debug(f'loaded model into memory -> {models["spacy"]}')
    yield
    
    models.clear()

app = FastAPI(lifespan=load_models)

@app.middleware('http')
async def monitoring_middleware(request:Request,function:Callable[[Request],Awaitable[Response]]) -> Response:
    request_id = uuid4().hex 
    request_datetime = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    response: Response = await function(request)
    response_time = round(time.perf_counter() - start_time, 4) 
    response.headers["X-Response-Time"] = str(response_time)
    response.headers["X-API-Request-ID"] = request_id 
    logger.debug(f'request_id:{request_id}| request_date:{request_datetime}| request_url:{request.url}| request_host:{request.client.host}| response_time:{response_time}| response_status_code:{response.status_code}')
    return response
    

@app.post("/upload")
async def file_upload_controller(
    file: Annotated[UploadFile, File(description="Uploaded PDF document")],
    pdf_processor:BackgroundTasks
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            detail=f"Only  PDFs are supported",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        file_path = await save_file(file)
        pdf_processor.add_task(extract_pdf, file_path)
        pdf_processor.add_task(vector_service.store_file_content_in_db,'./data/temp/'+file_path.split('\\')[-1]+'/'+file_path.split('\\')[-1].replace("pdf", "txt"),EMBED_URL,models,embed_semaphore_store)
    except Exception as e:
        raise HTTPException(
            detail=f"An error occurred while saving file - Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return {"filename": file.filename, "message": "File uploaded successfully"}

@app.post('/rag_search')
async def search_doc(request:RAGRequest):
    try:
        texts = await vector_service.get_content_from_db(text=request.query_string,url = EMBED_URL,search_semaphore=embed_semaphore_search)
    except Exception as e:
        logger.debug(f'Error in rag_search -> {str(e)}')
        raise HTTPException(
            detail=f"An error occurred while getting data from db - Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    if texts == [] or texts is None:
        return {'response':'there were no information about what you are asking, kindly submit the correct document and ask the right questions'}
    #return {'response':texts}
    context = texts
    question = request.query_string
    USER_PROMPT = f"""
    Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.

    <context>
    {context}
    </context>

    <question>
    {question}
    </question>"""
    logger.debug(f'the request to openai is {USER_PROMPT}')
    #async with httpx.AsyncClient() as client:
    #    response = await client.post(
    #        f"http://localhost:11434/api/chat", json={"model":"qwen3:0.6b","messages": [{"role": "user", "content": USER_PROMPT}],"stream":False},timeout=50.0
    #        )
    #response_op = json.loads(response.content.decode('utf-8'))
    #final_response = re.sub(r'<.*?>','',response_op['message']['content']).strip()
    response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": """You are a knowledgeable expert. Answer
                                        the user's query based only on the information provided in the
                                        context. If the answer is not in the context,
                                        say 'I couldn't find an answer to your question in the provided
                                        context.'"""},
        {
            "role": "user",
            "content": USER_PROMPT,
        },
    ],
    )
    final_response = response.choices[0].message.content
    return {'response':final_response}
