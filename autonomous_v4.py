import streamlit as st
import os
import uuid
import sqlite3
import requests
import json

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
def trigger_n8n_chain(chain: str, payload: dict) -> str:
    """
    Run multi-step n8n workflow chain
    Example: "email->crm->notify"
    """

    steps = chain.split("->")
    result = payload

    for step in steps:
        url = f"http://localhost:5678/webhook/{step.strip()}"
        res = requests.post(url, json=result)
        result = res.json() if "application/json" in res.headers.get("content-type","") else {"data": res.text}

    return str(result)

tools = [write_email, real_search, trigger_n8n_chain]


# ---------------- LLM ----------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ---------------- MEMORY (FIXED) ----------------
conn = sqlite3.connect("agent.db", check_same_thread=False)
memory = SqliteSaver(conn)


# ---------------- AGENT ----------------
agent = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt="""
    You are a workflow orchestration engine.

    You NEVER answer directly.

    You ONLY output JSON.

    RULES:

    1. Detect intent:
    - email
    - search
    - automation
    - multi-step automation

    2. Return ONLY this format:

{
  "workflow_type": "single | chain",
  "workflow": "write_email | real_search | trigger_n8n_chain",
  "chain": ["step1", "step2"],
  "payload": {}
}

    3. If single:
    - workflow + payload

    4. If chain:
    - workflow_type = "chain"
    - chain = steps array

    NO TEXT OUTPUT ALLOWED.
    """
    )


# ---------------- STREAMLIT UI ----------------
st.title("💣 FIXED AI AGENT (STABLE VERSION)")

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

        raw = result["messages"][-1].content

        # -------- SAFE PARSE --------
        try:
            decision = json.loads(raw)
        except:
            decision = {
                "workflow_type": "single",
                "workflow": "search",
                "payload": {"query": raw}
            }

        # -------- EXECUTION (FIXED) --------
        if decision.get("workflow_type") == "single":

            final = trigger_n8n_chain.invoke({
                "chain": decision.get("workflow", "search"),
                "payload": decision.get("payload", {})
            })

        else:

            final = trigger_n8n_chain.invoke({
                "chain": "->".join(decision.get("chain", [])),
                "payload": decision.get("payload", {})
            })

        st.markdown("### 🤖 AI Response")
        st.write(final)

        save_message(thread_id, "assistant", str(final))


# ---------------- HISTORY ----------------
st.markdown("## 🧾 Chat History")

history = load_history(thread_id)

for role, content in history:
    if role == "user":
        st.markdown(f"🧑‍💻 **You:** {content}")
    else:
        st.markdown(f"🤖 **AI:** {content}")