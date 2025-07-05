from elasticsearch import Elasticsearch
import aiofiles
from typing import AsyncGenerator, Any

import warnings

from loguru import logger

warnings.filterwarnings("ignore")


es_client = Elasticsearch(
    "https://192.168.1.87:9200",
    #ssl_assert_fingerprint='0D:11:23:13:1E:3F:3E:D3:94:08:B8:BE:63:7C:0B:E2:DF:DC:65:52:C4:50:81:2D:67:5D:FB:99:11:9D:61:31',
    verify_certs=False,
    basic_auth=("elastic", "password")
)

mappings = {
    "_source":{"excludes":["embeddings"]},
    "properties": {
        "file_name":{"type":"text"},
        "time_stamp":{"type":"text"},
        "doc_text":{"type":"text"},
        "embeddings": {
            "type": "dense_vector",
            "dims": 1024,
            "index": "true",
            "similarity": "dot_product",
        }
    }
}

es_client.indices.delete(index="search_index", ignore_unavailable=True)
es_client.indices.delete(index="book_index", ignore_unavailable=True)

# Create the index
es_client.indices.create(index="search_index", mappings=mappings)