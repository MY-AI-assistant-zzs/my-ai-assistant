import streamlit as st
st.set_page_config(page_title="我的私人AI助理",page_icon="🤖")
from pypdf import PdfReader
import requests
import datetime
st.title("贾维斯")
st.write("请在下方输入你的问题,我会认真回答。")
uploaded_file=st.sidebar.file_uploader("把你的秘密上传到这里",type=["txt","pdf"])
st.sidebar.info("目前支持.txt和.pdf格式")
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        reader=PdfReader(uploaded_file)
        text=""
        for page in reader.pages:
            page_text=page.extract_text()
            if page_text:
                text+=page_text
        st.session_state.doc_text=text
        st.success(f"PDF解析完成,共提取了{len(text)}个字符.")
    else:
        st.session_state.doc_text=uploaded_file.read().decode("utf-8",errors="ignore")
        st.success("文件读取成功!")
api_key="Bearer "+("API_KEY")
st.write("当前使用的key是:",api_key)
url = "https://api.deepseek.com/chat/completions"
if"doc_text"not in st.session_state:
    st.session_state.doc_text=""
if st.sidebar.button("清空聊天记录"):
    st.session_state.messages=[]
    st.balloons()
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":"你是一个有趣的人"}]
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
user_input = st.chat_input("请在这里输入你的问题：")
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    st.session_state.messages=st.session_state.messages[-10:]
    today=str(datetime.date.today())
    data = {
        "model":"deepseek-chat",
        "temperature":0.1,
        "messages":st.session_state.messages
    }
    data["messages"].insert(0,{"role":"system","content":"今天的日期是:"+today})
    if st.session_state.doc_text:
        data["messages"].insert(0,{"role":"system","content":"以下是我的文档内容,请基于它回答:"+st.session_state.doc_text})
    response = requests.post(url, headers=headers, json=data)
    print("====== 调试开始 ======")
    print("状态码:", response.status_code)
    print("原始内容:", response.text)
    print("======================")
    reply = response.json()['choices'][0]['message']['content']
    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
