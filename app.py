import streamlit as st
import json
import os
import base64
from dotenv import load_dotenv
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title="F1 테마 차 추천", page_icon="🏁", layout="centered")

def set_background(image_file_path):
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

# 로컬 이미지로 배경 설정
set_background("C:/Users/1/Downloads/f1.jpg")  # 여기에 네가 가진 이미지 파일 경로  # 여기에 네가 가진 이미지 파일 경로

# F1 로고 표시
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/320px-F1.svg.png", width=180)

# 레이싱 스타일 텍스트
st.markdown(
    """
    <h1 style="text-align: center; color: #e10600; font-family:Verdana;"><div style="display: inline-block; line-height: 1.2;">나만의 드림카! 🏎️<br>신차 추천 챗봇 🏁</div></h1>
    """,
    unsafe_allow_html=True
)
# 자동차 정보 불러오기
with open('data/hyundai.json', 'r', encoding='utf-8') as f:
    cars = json.load(f)

# 자동차 정보를 요약된 문장으로 변환
car_docs = []
for car in cars:
    doc = f"{car['brand']}의 {car['model_name']}은(는) {car['car_type']} 유형의 차량으로, {car['fuel_type']}을 사용하며, 가격은 약 {car['price']}만원입니다. 연비는 {car['fuel_efficiency']}km/l, 최대 주행 가능 거리는 {car['range_km']}km입니다. {car['seats']}인승이며, 사용 가능한 색상은 {', '.join(car['available_colors'])}입니다. 요약: {car['short_desc']}"
    car_docs.append(doc)

# 프롬프트 템플릿 설정
prompt_template = PromptTemplate.from_template(
    """당신은 자동차 추천 전문가입니다.
사용자의 요구나 상황, 취향 등을 고려해 아래 자동차 목록에서 가장 적합한 차량을 추천해주세요.

사용자 입력:
{user_input}

자동차 목록:
{car_documents}

가장 적절한 차량을 1~2개 추천하고, 추천 이유를 자연스럽게 설명해주세요."""
)

# LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini")

# 체인 설정 (LCEL 방식)
chain = prompt_template | llm

# Streamlit UI
#st.title("나에게 맞는 차 추천 챗봇")
st.markdown("### 🏁당신에게 맞는 최적의 차량을 찾아드립니다.")

user_input = st.text_input("어떤 차량을 찾고 계신가요?", placeholder="예: 전기차, 1인용, 예산 3천만 원 등")

if user_input: #엔터를 누르면 실행
    with st.spinner("추천 차량을 찾고 있어요..."):
        response = chain.invoke({
            "user_input": user_input,
            "car_documents": "\n".join(car_docs)
        })
        st.success("추천 완료!")
        st.markdown("### ✅ 추천 결과:")
        st.write(response.content)
