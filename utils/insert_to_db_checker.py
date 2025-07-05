import sys
sys.path.append('..')
sys.path.append('../rag_utils')
from rag_utils.service import vector_service
import asyncio
import time
import spacy

async def main():
    storeSemaphore = asyncio.Semaphore(10)
    models = {}
    models['spacy'] = spacy.load('../en_core_web_sm/en_core_web_sm/en_core_web_sm-3.8.0/',disable=['tagger','ner','lemmatizer','textcat'])
    await vector_service.store_file_content_in_db('C:\\Users\\Deepu\\Documents\\GitHub\\experiments\\app_llm_rag\data\\temp\\M2_Project_Report_v3.pdf\\M2_Project_Report_v3.txt','http://192.168.1.87:7788/embed',models=models,store_semaphore=storeSemaphore)
    #await asyncio.sleep(5)
    t0 = time.perf_counter()
    #results = await vector_service.get_content_from_db('Conclusions','http://192.168.1.87:9988/embed')
    #print('search time take is ',time.perf_counter()-t0)
    #print(results)
    
asyncio.run(main())