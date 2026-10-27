import streamlit as st
import requests
import datetime
from pypdf import PdfReader

st.set_page_config(page_title="我的私人AI助理", page_icon="🤖")
st.title("贾维斯")
st.write("请在下方输入你的问题，我会认真回答。")

api_input = st.sidebar.text_input("请输入你的API Key", type="password")
selected_role=st.sidebar.selectbox("请选择AI的角色", ["有趣的助手", "严谨的翻译官", "Python编程老师"])
ai_temp=st.sidebar.slider("设置AI的脑洞程度(温度),min_value=0.0,max_value=1.5,value=0.7,step=0.1")
if not api_input:
    st.warning("请先在左侧输入 API Key，否则无法对话！")
    st.stop()

uploaded_file = st.sidebar.file_uploader("把你的秘密上传到这里", type=["txt", "pdf"])
st.sidebar.info("目前支持 .txt 和 .pdf 格式")

if st.sidebar.button("清空聊天记录"):
    st.session_state.messages = []
    st.balloons()

if"messages"not in st.session_state:
    st.session_state.messages=[{"role":"system","content":"你现在扮演的角色是:"+selected_role}]
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        st.session_state.doc_text = text
    else:
        st.session_state.doc_text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.success("文件读取成功！")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_input = st.chat_input("请在这里输入你的问题：")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    st.session_state.messages = st.session_state.messages[-10:]
    
    today = str(datetime.date.today())
    temp_messages = list(st.session_state.messages)
    temp_messages.insert(0, {"role": "system", "content": "今天的日期是：" + today})
    
    if st.session_state.doc_text:
        temp_messages.insert(0, {"role": "system", "content": "以下是我的文档内容，请基于它回答：" + st.session_state.doc_text})

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_input,
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "temperature": max(0.0, min(1.5, float(ai_temp))),
        "messages": temp_messages
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        st.error("请求失败！状态码：" + str(response.status_code) + "，详情：" + response.text)
        st.stop()
        
    reply = response.json()['choices'][0]['message']['content']
    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
