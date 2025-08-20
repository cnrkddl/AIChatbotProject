from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory

import sqlite3


# ================================================================================================================================================================================


# 환경변수 불러오기
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

# LLM 구성
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# 역할 부여용 시스템 프롬프트
system_prompt = SystemMessagePromptTemplate.from_template(
    """
당신은 요양병원에 있는 치매 환자의 보호자를 위한 감정케어 챗봇입니다.
보호자는 환자와 떨어져 있으며, 환자의 상태가 걱정되어 정서적으로 힘들 수 있습니다.
보호자의 감정을 따뜻하게 받아들이고 공감하며, 필요한 경우 간단한 조언이나 위로를 제공합니다.
보호자가 챗봇의 기능이나 역할을 묻는 질문이 있을 경우, 스스로의 역할과 한계를 따뜻하게 설명하고 신뢰를 줄 수 있는 답변을 제공합니다.

보호자가 "환자의 상태를 묻는 질문"을 할 경우, 챗봇은 직접 상태를 설명하지 않습니다. 
대신 '환자 상태 정보' 페이지를 안내하거나 병원 간호사에게 연락할 수 있도록 도와주세요.

예: 
"환자분의 구체적인 상태는 '환자 상태 정보' 페이지에서 확인하실 수 있어요. 
추가 문의가 필요하시면 병원 간호사 선생님께 연락 부탁드려요. 📞 031-919-0041"



일정 문의(예: 식사 시간, 면회 시간, 목욕 요일 등)에 대해서는 병동 상황에 따라 변경될 수 있어 챗봇이 정확히 안내하기 어렵습니다.
이 경우 보호자에게 일정이 유동적임을 이해시키고, 병원 간호사에게 직접 문의할 수 있도록 안내하세요.

예: 
"해당 일정은 병동 내 상황에 따라 변경될 수 있어 정확한 시간 안내는 어려워요. 
자세한 내용은 병원 간호사 선생님께 직접 문의해 주시면 안내해드릴 수 있을 거예요. 📞 031-919-0041"

단, 감정 표현, 일정 문의, 시스템 질문 등은 환자 상태 안내와 혼동되지 않도록 따뜻하게 응답하세요.
""".strip())



# ================================================================================================================================================================================




# Few-shot 예시 정의
example_prompt = PromptTemplate(
    input_variables=["input", "intent", "response"],
    template="사용자의 질문: {input}\n→ 의도: {intent}\n→ 응답 예시: {response}\n"
)

examples = [
    {
        "input": "어머니 오늘 컨디션은 어떤가요?",
        "intent": "상태 확인",
        "response":""
    },
    {
        "input": "괜히 죄책감이 드네요…",
        "intent": "감정 표현",
        "response":""
    },
    {
        "input": "어머니가 넘어지셨다는 말은 못 들었는데 괜찮으신가요?",
        "intent": "상태 확인",
        "response":""
    },
    {
        "input": "오늘 식사 시간은 언제였죠?",
        "intent": "일정 문의",
        "response":""
    },
    {
        "input": "혹시 더 나빠진 건 아닌가요?",
        "intent": "불안 호소",
        "response": (
            "많이 걱정되셨죠. 환자분의 상태가 조금만 달라 보여도 보호자님 입장에선 불안하실 수 있어요.\n"
            "그런 걱정이 드는 건 너무나 자연스러운 일이에요.\n"
            "병원에서도 환자분의 상태를 지속적으로 잘 살피고 있으니 너무 염려하지 않으셔도 괜찮아요."
        )
    },
    {
        "input": "챗봇은 왜 이런 질문은 대답 못해요?",
        "intent": "시스템 질문",
        "response": (
            "저는 요양병원 보호자님을 위한 감정 케어 챗봇이에요.\n"
            "보호자님이 멀리 계셔도 마음을 표현하실 수 있도록 돕고,\n"
            "환자분의 상태를 간단히 전달드리기 위해 만들어졌어요.\n\n"
            "환자 상태는 병원 기록(EMR)을 기반으로 요약해서 전달드리며,\n"
            "실제 진단이나 의료 상담은 병원에서 진행해 주셔야 해요."
        )
    },
    {
        "input": "문자 알림은 왜 안 오나요?",
        "intent": "시스템 질문",
        "response": (
            "문자 알림은 병원 내 별도 시스템을 통해 발송되는 경우가 많아,\n"
            "챗봇에서는 직접 확인하거나 수정이 어려운 점 양해 부탁드려요.\n"
            "정확한 확인을 원하시면 병원에 문의해 주시면 빠르게 도와드릴 수 있을 거예요.\n"
            "📞 031-919-0041"
        )
    }
]

few_shot = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="다음은 보호자님의 질문과 그에 따른 의도 분류 예시입니다.\n",
    suffix="",
    input_variables=[]
)



# ================================================================================================================================================================================



# HumanMessage를 더 명확하게 수정!
human_message = HumanMessagePromptTemplate.from_template(
    "다음 보호자의 질문에 대해 따뜻하게 공감하고 적절한 위로와 조언을 해주세요:\n{user_input}"
)


# PromptTemplate 구성
prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    SystemMessage(content=few_shot.format()),  # user_input 안 쓰니 format()만
    human_message,
])


memory_store = {}

def get_session_history(session_id: str):
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(return_messages=True)
    return memory_store[session_id].chat_memory


chat_chain = RunnableWithMessageHistory(
    prompt | llm,
    get_session_history=get_session_history,
    input_messages_key="user_input",
    history_messages_key="history"
)

# ----------------------------------------------------------------------------------------------------------

# DB 초기화
db_path = os.path.join(os.path.dirname(__file__), "chat_logs", "chat_logs.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_log (
    session_id TEXT,
    user_input TEXT,
    bot_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_chat(session_id, user_input, bot_response):
    cursor.execute(
        "INSERT INTO chat_log (session_id, user_input, bot_response) VALUES (?, ?, ?)",
        (session_id, user_input, bot_response)
    )
    conn.commit()

def get_emotional_support_response(session_id: str, user_input: str):
    reply = chat_chain.invoke(
        {"user_input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

    # ✅ 응답 직후 DB 저장
    save_chat(session_id, user_input, reply.content)

    return reply.content