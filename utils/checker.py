import sys
sys.path.append('..')
from rag_utils.transform import clean, load, embed

import asyncio
import spacy
import tiktoken as tk
import time
import os

def count_tokens(string: str, encoding_name="cl100k_base") -> int:
    # Get the encoding
    encoding = tk.get_encoding(encoding_name)
    
    # Encode the string
    encoded_string = encoding.encode(string, disallowed_special=())

    # Count the number of tokens
    num_tokens = len(encoded_string)
    return num_tokens


def split_sentences_by_spacy(text, max_tokens, 
                        overlap=0
                        ):
    # Load spaCy model
    nlp = spacy.load('./en_core_web_sm/en_core_web_sm/en_core_web_sm-3.8.0/')
        
    doc = nlp(text,disable=['tagger','ner','lemmatizer','textcat'])
    
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

async def get_data(file_name:str) -> list[str]:
    final_chunks = []
    if os.path.getsize(filename=file_name) == 0:
        return None
    async for chunks in load(file_name):
        cleaned = await asyncio.to_thread(clean,chunks)
        t0 = time.perf_counter()
        spacy_chunks = await asyncio.to_thread(split_sentences_by_spacy,cleaned,256,0)
        print(f'finished processing, and the time it took is {time.perf_counter() - t0:.4f}')
        final_chunks.append(spacy_chunks)
    return final_chunks
        
        
        
async def main():
    t0 = time.perf_counter()
    #len_1 = await get_data('./data/temp/M2_Project_Report_v3.txt')
    len_2 = await get_data('./data/tempdesign_ai-report.pdf/design_ai-report.txt')
    #print(len_1[0])
    print('value is ',len_2)
    print(f'total time taken is -> {time.perf_counter() - t0:.4f}')
    
asyncio.run(main())