import streamlit as st
import os
import uuid
from datetime import datetime
import sqlite3
import requests

from openaiapikey import apikey

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from duckduckgo_search import DDGS

os.environ["OPENAI_API_KEY"] = apikey

# ====================== DATABASE ======================
conn = sqlite3.connect("agent.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    thread_id TEXT,
    role TEXT,
    content TEXT,
    created_at TEXT
)
""")
conn.commit()

def save_message(thread_id, role, content):
    conn.execute(
        "INSERT INTO chat_history VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), thread_id, role, content, datetime.now().isoformat())
    )
    conn.commit()

def load_history(thread_id):
    cur = conn.execute(
        "SELECT role, content FROM chat_history WHERE thread_id=? ORDER BY created_at",
        (thread_id,)
    )
    return cur.fetchall()

# ====================== TOOLS ======================
@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=4)
        return "\n\n".join([f"**{r['title']}**\n{r['body'][:300]}..." for r in results])
    except:
        return "Search failed."

@tool
def send_email(topic: str, recipient: str = "default") -> str:
    """Trigger n8n to send email"""
    try:
        payload = {
            "topic": topic,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat()
        }
        # آدرس webhook n8n خودت رو بذار
        url = "http://localhost:5678/webhook/send-email"   # تغییر بده
        res = requests.post(url, json=payload, timeout=10)
        return f"Email trigger sent. Status: {res.status_code}\n{res.text[:200]}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

tools = [web_search, send_email]

# ====================== LLM & AGENT ======================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

memory = SqliteSaver(conn)

agent = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    # prompt رو ساده‌تر و هوشمندتر کن
    prompt="""You are a helpful AI assistant that uses tools when necessary.
    - For search requests → use web_search
    - For email requests → use send_email
    Be concise and accurate."""
)

# ====================== STREAMLIT ======================
st.title("💣 My AI Agent v2")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

thread_id = st.session_state.thread_id

user_input = st.text_input("Ask me anything:")

if user_input:
    save_message(thread_id, "user", user_input)

    with st.spinner("Thinking..."):
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        final_answer = result["messages"][-1].content

    save_message(thread_id, "assistant", final_answer)
    st.markdown("### 🤖 Response:")
    st.write(final_answer)

# History
st.markdown("## Chat History")
for role, content in load_history(thread_id):
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Agent:** {content}")