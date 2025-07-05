import sys

sys.path.append('..')

from models.schema import RAGRequest,RAGSearchUtils
import asyncio
from fastapi import HTTPException,status, Body

from .service import vector_service

async def get_rag_text(rag_search_utils:dict,request:RAGRequest = Body(...)) -> list[str]:
    try:
        texts = await vector_service.get_content_from_db(text=request.query_string,url = rag_search_utils['embed_url'],search_semaphore=rag_search_utils['semaphore'])
    except Exception as e:
        raise HTTPException(
            detail=f"An error occurred while getting data from db - Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    