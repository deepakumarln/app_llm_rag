import requests
import streamlit as st
from loguru import logger
import json
import re

st.title("Some ChatBot") 

st.write("Upload a file")
file = st.file_uploader("Choose file", type=["pdf"])

if st.button("Submit"):
    if file is not None:
        files = {"file": (file.name, file, file.type)}
        response = requests.post("http://192.168.1.87:8899/upload", files=files)
        st.write(response.text)
    else:
        st.write("No file uploaded.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Write your prompt in this input field"): 
    st.session_state.messages.append({"role": "user", "content": prompt}) 

    with st.chat_message("user"):
        st.text(prompt)

    response = requests.post(f'http://192.168.1.87:8899/rag_search',json={'query_string':prompt},timeout=55.0)
    
    response.raise_for_status()
    data = json.loads(response.text)
    print(data)

    with st.chat_message("assistant"):
        #st.markdown(re.sub(r'<.*?>','',data['response']))
        st.markdown(data['response'])
    st.session_state.messages.append({"role": "assistant", "content": data['response']}) 