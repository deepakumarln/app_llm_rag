import sys
sys.path.append('..')
sys.path.append('../rag_utils')
from rag_utils.service import vector_service
import asyncio
import time


async def main():
    #await vector_service.store_file_content_in_db('C:\\Users\\Deepu\\Documents\\GitHub\\experiments\\app_llm_rag\data\\temp\\M2_Project_Report_v3.pdf\\M2_Project_Report_v3.txt','http://192.168.1.87:9988/embed',{})
    t0 = time.perf_counter()
    searchSemaphore = asyncio.Semaphore(10)
    results = await vector_service.get_content_from_db('Named Entity','http://192.168.1.87:7788/embed',search_semaphore=searchSemaphore)
    print('search time take is ',time.perf_counter()-t0)
    print(results)
    
asyncio.run(main())