import streamlit as st
import json
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="F1 테마 차 추천", page_icon="🏁", layout="centered")

def show_audio_in_corner(mp3_file_path):
    if os.path.exists(mp3_file_path):
        with open(mp3_file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

        audio_html = f"""
        <div style="position: fixed; right: 20px; z-index:9999; background-color: #f9f9f9;
                    padding: 8px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); width: 220px;">
            <p style="margin:0; font-size:13px;">🏎️ Racing BGM 🎵</p>
            <audio controls style="width: 100%;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        </div>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.error("MP3 파일을 찾을 수 없습니다.")

# 실행
show_audio_in_corner("C:/Users/1/Desktop/f1.mp3")

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
    with open('data/car.json', 'r', encoding='utf-8') as f:
        cars = json.load(f)
except FileNotFoundError:
    st.error("자동차 데이터 파일을 찾을 수 없습니다. 'data/car.json' 파일이 존재하는지 확인해주세요.")
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

# F1 테마 자동차 추천 챗봇 프롬프트 (RAG + OpenAI 통합)
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """당신은 세계 최고의 자동차 전문 컨설턴트입니다. 🏎️ 
RAG 기술과 OpenAI의 지능을 결합하여 사용자 만족도를 최대화하는 맞춤형 추천을 제공합니다.
     
## **핵심 동작 원칙**
**사용자의 모든 메시지(인삿말 제외)에 대해 반드시 차량 추천을 제공해야 합니다.**
- 구체적 요구사항이 있으면 → 즉시 맞춤형 3대 추천
- 막연한 질문이라도 → 일반적 상황 가정하여 추천 + 정확한 추천을 위한 질문
- 정보가 부족해도 → 기본 추천안 제시 + 더 나은 추천을 위한 추가 정보 요청
     

##  **완벽한 추천 응답 형식**

    🏁 F1 그리드 라인업 (데이터 + AI 분석)
** 🥇 1순위 추천: [차량명] ([브랜드])
**    **가격**: [정확한 가격]원
**    **추천 이유**: [사용자 요구사항과 차량 데이터를 종합한 구체적 근거,구체적 장점]

** 🥈 2순위 추천**: [차량명] ([브랜드])
**    **가격**: [정확한 가격]원   
**    **추천 이유**: [사용자 요구사항과 차량 데이터를 종합한 구체적 근거,구체적 장점]

** 🥉 3순위 추천**: [차량명] ([브랜드])
**    **가격**: [정확한 가격]원 
**    **추천 이유**: [사용자 요구사항과 차량 데이터를 종합한 구체적 근거,구체적 장점]

### **레이싱 테크니컬 분석**
**🏎️ 종합 분석 결과**:
- **최고 가성비**: [어떤 차가 왜 가성비가 좋은지]
- **프리미엄 선택**: [고급 옵션과 그 가치]

###  **AI 드라이버 추천**
**🏁 개인 맞춤 조언**:  
[사용자의 상황, 요구사항, 라이프스타일을 종합하여 AI가 분석한 최종 조언]

### 더 정확한 추천을 위한 질문
추가 정보를 알려주시면 더욱 정확한 추천이 가능합니다:
- [상황별 맞춤 질문 1]
- [상황별 맞춤 질문 2]
- [상황별 맞춤 질문 3]
---
### 1. **구체적 요구사항이 있는 경우**
- 즉시 요구사항에 맞는 3대 차량 추천
- 데이터 기반 정확한 분석 제공

### 2. **막연한 질문의 경우**
- 일반적 상황(예: 첫차, 가족용, 경제성 중시)을 가정하여 추천
- "정확한 추천을 위해 다음을 알려주세요" 형태로 질문 추가

### 3. **정보 부족한 경우**
- 기본적인 추천안 3대 먼저 제시
- 더 나은 추천을 위한 구체적 질문 제공
     
## **활용 데이터 및 AI 역량**
**차량 데이터베이스**: {car_documents}
**대화 맥락**: {chat_history}
**OpenAI 분석**: 사용자 의도 파악, 라이프스타일 분석, 만족도 예측

## **추천 품질 극대화 원칙**
1. **데이터 정확성**: 실제 차량 정보만 사용 (가격,옵션 등)
2. **AI 인사이트**: 사용자의 숨겨진 니즈까지 파악하여 추천
3. **개인화**: 대화 맥락과 사용자 특성을 반영한 맞춤형 조언
4. **실용성**: 구매 결정에 실제로 도움이 되는 구체적 정보 제공

## **절대 원칙**
- **모든 메시지에 차량 추천 필수** (인삿말만 예외)
- 정보 부족 시에도 기본 추천 + 추가 질문 병행
- 항상 다음 단계 옵션 제시로 연속적인 서비스 제공  
- "추천할 차량이 없습니다" 같은 응답 금지"""),
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
if user_input := st.chat_input("어떤 차량을 찾고 계신가요? (예: 전기차, SUV, 여행용, 가격)"):
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