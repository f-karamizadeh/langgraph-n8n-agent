import streamlit as st
import os
import uuid
import sqlite3
import requests

from datetime import datetime

from openaiapikey import apikey

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from duckduckgo_search import DDGS

# ---------------- API KEY ----------------
os.environ["OPENAI_API_KEY"] = apikey


# ---------------- DATABASE ----------------
conn = sqlite3.connect("agent.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT,
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


# ---------------- TOOLS ----------------
@tool
def write_email(topic: str) -> str:
    """Create a formal email"""
    return f"""Subject: {topic}

Dear Sir/Madam,

I am writing regarding {topic}.

Best regards,
AI Agent
"""


@tool
def real_search(query: str) -> str:
    """Search web"""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

    return "\n".join([f"{r['title']} - {r['body']}" for r in results])


@tool
def trigger_n8n(workflow: str, payload: dict) -> str:
    """Call n8n webhook"""

    workflow = workflow.lower().strip()   # 👈 اینجا اضافه کن

    workflow_map = {
        "email": "write_email"
    }


    endpoint = workflow_map.get(workflow)

    if not endpoint:   # 👈 این هم اضافه کن
        return f"Invalid workflow: {workflow}"
    
    url = f"http://localhost:5678/webhook/{endpoint}"

    print("*****************WORKFLOW:****************", workflow, flush=True)
    print("*****************ENDPOINT:****************", endpoint, flush=True)
    print("*****************URL:****************", url, flush=True)

    try:
        res = requests.post(url, json=payload)
        return res.text
    except Exception as e:
        return f"ERROR: {str(e)}"
    
    
tools = [write_email, real_search, trigger_n8n]


# ---------------- LLM ----------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([trigger_n8n, real_search])


# ---------------- MEMORY (FIXED) ----------------

memory = SqliteSaver(conn)


# ---------------- AGENT ----------------
agent = create_react_agent(
    llm,
    [ trigger_n8n,real_search],
    checkpointer=memory,
    prompt="""
You are a strict tool-using agent.

RULES:

1. If user wants email:
   You MUST call trigger_n8n exactly like this:
   trigger_n8n(workflow="email", payload={"topic": "<user request>"})

2. If user wants search:
   You MUST call real_search(query)

3. NEVER answer without tools.

4. NEVER skip arguments.

5. If you cannot call tool correctly → try again one more time.

Return only final answer or error message.
"""
)
# ---------------- STREAMLIT UI ----------------
st.title("💣  MY LangGraph AI AGENT ")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

thread_id = st.session_state.thread_id


# ---------------- INPUT ----------------
user_input = st.text_input("Ask anything:")


# ---------------- MAIN LOGIC ----------------
if user_input:

    save_message(thread_id, "user", user_input)

    with st.spinner("Thinking..."):

        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": thread_id}}
        )

        # خروجی امن
        if isinstance(result, dict) and "messages" in result:
            final_answer = result["messages"][-1].content
        else:
            final_answer = str(result)

    save_message(thread_id, "assistant", final_answer)

    st.markdown("### 🤖 AI Response")
    st.write(final_answer)

# ---------------- HISTORY ----------------
st.markdown("## 🧾 Chat History")

history = load_history(thread_id)

for role, content in history:
    if role == "user":
        st.markdown(f"🧑‍💻 **You:** {content}")
    else:
        st.markdown(f"🤖 **AI:** {content}")