import streamlit as st
import os

from openaiapikey import apikey
from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


# ---------------- API KEY ----------------
os.environ["OPENAI_API_KEY"] = apikey


# ---------------- TOOLS ----------------
@tool
def write_email(topic: str) -> str:
    """Write a formal email"""
    return f"""
Subject: {topic}

Dear Sir/Madam,

I am writing regarding {topic}.

I would appreciate your response.

Best regards,
AI Agent
"""


@tool
def search_info(query: str) -> str:
    """Simple search tool (mock)"""
    return f"Search result for: {query}"


tools = [write_email, search_info]


# ---------------- LLM ----------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ---------------- MEMORY ----------------
memory = MemorySaver()


# ---------------- AGENT (NEXT LEVEL) ----------------
agent = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt=(
        "You are an autonomous AI agent. "
        "Think step by step. "
        "Use tools only when needed. "
        "Be concise and intelligent."
    )
)


# ---------------- STREAMLIT UI ----------------
st.title("🧠 Autonomous Agent v2")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ✅ این خط باید حتماً وجود داشته باشه
user_input = st.text_input("Ask anything:")


if user_input:

    result = agent.invoke(
        {
            "messages": [HumanMessage(content=user_input)]
        },
        config={
            "configurable": {
                "thread_id": "user-1"
            }
        }
    )

    answer = result["messages"][-1].content

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("AI", answer))


# display chat
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"🧑‍💻 {msg}")
    else:
        st.markdown(f"🤖 {msg}")
# ---------------- CHAT DISPLAY ----------------
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"🧑‍💻 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")