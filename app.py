import streamlit as st
import json
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
import pandas as pd
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="F1 테마 차 추천", page_icon="🏁", layout="centered")

def set_background(image_file_path):
    if os.path.exists(image_file_path):
        with open(image_file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)

# 로컬 이미지로 배경 설정 (파일이 존재할 때만)
set_background("C:/Users/1/Downloads/f1.jpg")

# F1 로고 표시
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/320px-F1.svg.png", width=180)

# 레이싱 스타일 텍스트
st.markdown(
    """
    <h1 style="text-align: center; color: #e10600; font-family:Verdana; font-size: 48px;"><div style="display: inline-block; line-height: 1.2;">나만의 드림카! 🏎️<br>신차 추천 챗봇 🏁</div></h1>
    """,
    unsafe_allow_html=True
)

# 자동차 정보 불러오기
try:
    with open('data/hyundai.json', 'r', encoding='utf-8') as f:
        cars = json.load(f)
except FileNotFoundError:
    st.error("자동차 데이터 파일을 찾을 수 없습니다. 'data/hyundai.json' 파일이 존재하는지 확인해주세요.")
    st.stop()

# 자동차 정보를 요약된 문장으로 변환
car_docs = []
for car in cars:
    doc = f"{car['brand']}의 {car['model_name']}은(는) {car['car_type']} 유형의 차량으로, {car['fuel_type']}을 사용하며, 가격은 약 {car['price']}만원입니다. 연비는 {car['fuel_efficiency']}km/l, 최대 주행 가능 거리는 {car['range_km']}km입니다. {car['seats']}인승이며, 사용 가능한 색상은 {', '.join(car['available_colors'])}입니다. 요약: {car['short_desc']}"
    car_docs.append(doc)

# CSV 저장 파일 경로
chat_history_csv_path = "chat_history.csv"

# 사용자 아이디 입력 및 세션 초기화
if "user_id" not in st.session_state or st.session_state["user_id"] is None:
    st.markdown('<p style="color: white; font-size: 24px; font-weight: bold;">이름 또는 닉네임을 입력해주세요 🚗 </p>', unsafe_allow_html=True)
    user_id_input = st.text_input("닉네임 입력", placeholder="닉네임을 입력하세요", label_visibility="hidden")
    if user_id_input:
        st.session_state["user_id"] = user_id_input
        st.rerun()
    st.stop()

user_id = st.session_state["user_id"]

# 채팅 기록 초기화 및 사용자 상태 확인
if "messages" not in st.session_state:
    st.session_state.messages = []
    is_existing_user = False
    
    # CSV에서 기존 사용자 메시지 불러오기
    if os.path.exists(chat_history_csv_path):
        try:
            df = pd.read_csv(chat_history_csv_path)
            user_msgs_df = df[df["user_id"] == user_id]
            if not user_msgs_df.empty:
                is_existing_user = True
                for _, row in user_msgs_df.iterrows():
                    st.session_state.messages.append({"role": "user", "content": row["content"]})
        except Exception as e:
            st.warning(f"기존 채팅 기록을 불러오는 중 오류가 발생했습니다: {e}")
    
    # 사용자 상태에 따른 환영 메시지
    if is_existing_user:
        st.markdown(f'<h3 style="color: white; font-size: 28px; font-weight: bold;">🏁 {user_id}님, 다시 오셨네요! 이전 대화를 불러왔습니다.</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #ffcc00; font-size: 20px; font-weight: bold;">⬇️ 아래에서 이전 대화 내용을 확인하실 수 있습니다!</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<h3 style="color: white; font-size: 28px; font-weight: bold;">🏁 {user_id}님, 처음 오셨네요! 환영합니다!</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #ffcc00; font-size: 20px; font-weight: bold;">💬 아래 채팅창에 원하시는 차량 조건을 말씀해주세요!</p>', unsafe_allow_html=True)
else:
    # 세션이 이미 있는 경우 (페이지 새로고침 등)
    st.markdown(f'<h3 style="color: white; font-size: 24px;">🏁 {user_id}님, 당신에게 맞는 최적의 차량을 추천하겠습니다!</h3>', unsafe_allow_html=True)

# 프롬프트 템플릿 정의
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """당신은 자동차 추천 전문가입니다. 
    
사용자의 이전 대화 기록과 최근 입력을 종합적으로 고려하여 가장 적절한 차량을 3순위 추천하고 추천 이유를 자연스럽게 설명해주세요.

자동차 목록:
{car_documents}

이전 대화 기록:
{chat_history}"""),
    ("human", "{user_input}")
])

# LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini")

# 체인 생성 (LCEL)
chain = prompt_template | llm

# 채팅 기록을 문자열로 변환하는 함수
def format_chat_history():
    if not st.session_state.messages:
        return "이전 대화 기록이 없습니다."
    
    history_text = ""
    for i, msg in enumerate(st.session_state.messages, 1):
        history_text += f"{i}. 사용자: {msg['content']}\n"
    return history_text

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if user_input := st.chat_input("어떤 차량을 찾고 계신가요? (예: 전기차, SUV)"):
    # 사용자 메시지를 채팅 기록에 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 사용자 메시지 화면 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner(""):
        # 스피너 텍스트를 직접 표시 (흰색)
        spinner_placeholder = st.empty()
        spinner_placeholder.markdown('<p style="color: white; font-size: 16px; font-weight: bold;">차량을 추천하는 중입니다 🏎️ 🏎️ 🏎️</p>', unsafe_allow_html=True)
        try:
            # 체인 실행
            inputs = {
                "user_input": user_input,
                "car_documents": "\n".join(car_docs),
                "chat_history": format_chat_history()
            }
            response = chain.invoke(inputs)
            bot_reply = response.content
            
        except Exception as e:
            bot_reply = f"죄송합니다. 추천 과정에서 오류가 발생했습니다: {e}"

    # 사용자 입력을 CSV에 저장
    try:
        new_row = {"user_id": user_id, "content": user_input}
        header_flag = not os.path.exists(chat_history_csv_path)
        pd.DataFrame([new_row]).to_csv(chat_history_csv_path, mode="a", index=False, header=header_flag, encoding='utf-8')
    except Exception as e:
        st.warning(f"채팅 기록 저장 중 오류가 발생했습니다: {e}")

    # 챗봇 응답 출력 (흰색 글씨로 표시)
    with st.chat_message("assistant"):
        st.markdown(f'<div style="color: white; font-size: 20px;">{bot_reply}</div>', unsafe_allow_html=True)