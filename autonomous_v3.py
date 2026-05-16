import streamlit as st
import os
import uuid

from openaiapikey import apikey
from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from duckduckgo_search import DDGS
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


# ---------------- API KEY ----------------
os.environ["OPENAI_API_KEY"] = apikey


# ---------------- TOOLS ----------------
@tool
def write_email(topic: str) -> str:
    """Write formal email"""
    return f"""
Subject: {topic}

Dear Sir/Madam,

I am writing regarding {topic}.

Best regards,
AI Agent
"""


@tool
def search_info(query: str) -> str:
    """Search information"""
    return f"Search result for: {query}"


@tool
def real_search(query: str) -> str:
    """Search the web for real information"""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

    output = ""
    for r in results:
        output += f"{r['title']} - {r['body']}\n"

    return output


import requests


@tool
def trigger_n8n(data: str) -> str:
    """Send data to n8n webhook"""
    url = "http://localhost:5678/webhook/test"

    res = requests.post(url, json={"data": data})

    return f"n8n response: {res.text}"


tools = [write_email, real_search, trigger_n8n]


# ---------------- LLM ----------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ---------------- MEMORY ----------------
conn = sqlite3.connect("agent.db", check_same_thread=False)
memory = SqliteSaver(conn)


# ---------------- PLANNER AGENT ----------------
planner = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt="""
You are a planning agent.

Your job:
- Break the user request into steps
- Decide what needs to be done
- Do NOT execute tools

Return a clear plan.
""",
)


# ---------------- EXECUTOR AGENT ----------------
executor = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt="""
You are an execution agent.

Your job:
- Execute the plan step by step
- Use tools when needed
- Produce results
""",
)


# ---------------- CRITIC AGENT ----------------
critic = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt="""
You are a critic agent.

Your job:
- Review the result
- Improve it if needed
- Return a clean final answer
""",
)


# ---------------- STREAMLIT UI ----------------
st.title("💣 Autonomous Multi-Agent System v3")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


user_input = st.text_input("Ask anything:")

response_placeholder = st.empty()

if user_input:

    thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
    with st.spinner("🧠 Agent is thinking..."):

     # -------- PLAN --------
     plan_stream = planner.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=thread_config
     )

     plan_text = ""

     for chunk in plan_stream:
        if isinstance(chunk, dict):
            if "agent" in chunk:
                plan_text = chunk["agent"]["messages"][-1].content

     response_placeholder.markdown(f"🧠 Planning...\n\n{plan_text}")

     # -------- EXECUTE --------
     execution_stream = executor.stream(
        {"messages": [HumanMessage(content=plan_text)]},
        config=thread_config
     )

     execution_text = ""

     for chunk in execution_stream:
        if isinstance(chunk, dict):
            if "agent" in chunk:
                execution_text = chunk["agent"]["messages"][-1].content

     response_placeholder.markdown(f"🔧 Executing...\n\n{execution_text}")

     # -------- CRITIC --------
     final_stream = critic.stream(
        {"messages": [HumanMessage(content=execution_text)]},
        config=thread_config
     )

     final_answer = ""

     for chunk in final_stream:
        if isinstance(chunk, dict):
            if "agent" in chunk:
                final_answer = chunk["agent"]["messages"][-1].content

     response_placeholder.markdown(f"🧐 Reviewing...\n\n{final_answer}")
    

     # -------- EXECUTE --------
     execution_stream = executor.stream(
            {"messages": [HumanMessage(content=plan_text)]}, config=thread_config
     )

     execution_text = ""

     for chunk in execution_stream:
      if isinstance(chunk, dict):
        if "agent" in chunk:
            execution_text = chunk["agent"]["messages"][-1].content
        elif "output" in chunk:
            execution_text = chunk["output"]
        elif "messages" in chunk:
            execution_text = chunk["messages"][-1].content

            response_placeholder.markdown(f"🔧 Executing...\n\n{execution_text}")
        # -------- CRITIC --------
        final_stream = critic.stream(
            {"messages": [HumanMessage(content=execution_text)]}, config=thread_config
        )

        final_answer = ""
        final_answer = ""

        for chunk in final_stream:
            if isinstance(chunk, dict):
                if "agent" in chunk:
                    final_answer = chunk["agent"]["messages"][-1].content
                elif "output" in chunk:
                    final_answer = chunk["output"]
                elif "messages" in chunk:
                    final_answer = chunk["messages"][-1].content

    response_placeholder.markdown(f"🧐 Reviewing...\n\n{final_answer}")

    # -------- FINAL OUTPUT --------
    if final_answer:
        st.success("✅ Final Answer:")
        st.write(final_answer)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", final_answer))
    else:
        st.error("❌ No final answer generated")
# ---------------- DISPLAY ----------------
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"🧑‍💻 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")
