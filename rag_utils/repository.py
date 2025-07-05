from loguru import logger
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan, async_bulk

import asyncio


class ElasticRepository:
    def __init__(self, host: str = "localhost", port: int = 9200) -> None:
        self.elastic_client = AsyncElasticsearch(
    hosts=[{"host":host,"port":port,"scheme":"https"}],
    verify_certs=False,
    basic_auth=("elastic", "password"),
    )
        
    async def insert(self,index_name:str,data:dict):
        push_data = []
        push_data.append(data)
        logger.debug(f'pushing data into elastic')
        def gen_data():
            for i in push_data:
                yield {
                "_index": "search_index",
                "file_name": i['file_name'],
                "time_stamp":i['time_stamp'],
                "doc_text": i['doc_text'],
                "embeddings": i['embeddings']
            }

        await async_bulk(self.elastic_client,gen_data())
        logger.debug(f'pushing data into elastic completed!')
    
        
    async def search(self,index_name:str,text:str,embeddings:list[float]):
        logger.debug(f'scanning index for document(s)')
        async for doc in async_scan(
            client=self.elastic_client, index=index_name, knn={
            "field": "embeddings",
            "query_vector": embeddings,
            "k": 5,
            "num_candidates": 5,
        }
        ):
            
            #logger.debug(f"Search Query Results are file_name -> {doc['_source']['file_name']}, time_stamp -> {doc['_source']['time_stamp']}, text -> {doc['_source']['doc_text']}")
            yield {"file_name":doc['_source']['file_name'],"time_stamp":doc['_source']['time_stamp'],"text":doc['_source']['doc_text']}
        
#async for doc in async_scan(
#        client=es,
#        query={"query": {"match": {"title": "python"}}},
#        index="orders-*"
#    ):