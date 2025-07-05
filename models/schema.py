from pydantic import BaseModel
from asyncio import Semaphore

class RAGRequest(BaseModel):
    query_string:str
    
class EmbeddingData(BaseModel):
    text:str
    url:str
    
class RAGSearchUtils(BaseModel):
    #semaphore:Semaphore
    embed_url:str
    
