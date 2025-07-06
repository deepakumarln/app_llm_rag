import sys
sys.path.append('..')
sys.path.append('../rag_utils')
from rag_utils.service import vector_service
import asyncio
import time

'''code checker for elastic search'''
async def main():
    t0 = time.perf_counter()
    searchSemaphore = asyncio.Semaphore(10)
    results = await vector_service.get_content_from_db('Named Entity','http://192.168.1.87:7788/embed',search_semaphore=searchSemaphore)
    print('search time take is ',time.perf_counter()-t0)
    print(results)
    
asyncio.run(main())