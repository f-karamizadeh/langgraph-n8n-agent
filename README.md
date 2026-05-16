# 🤖 Autonomous AI Agent + n8n Automation System

A fully autonomous AI system built with **LangGraph, OpenAI, Streamlit, and n8n** that can reason, use tools, and trigger real-world automation workflows.

---

## 🚀 What this project does

This system allows an AI agent to:

- 🧠 Make autonomous decisions using LangGraph
- 📧 Generate and send emails via n8n webhook
- 🌐 Perform real-time web search
- 💾 Store conversation history in SQLite
- 🔗 Trigger external automation workflows (n8n)

---

## 🧱 System Architecture

```
User → Streamlit UI (autonomous.py)
           ↓
     LangGraph AI Agent
           ↓
   ┌────────┼─────────┐
   │        │         │
Search   Email     n8n Webhook
(DuckDuckGo)   (write_email)
           ↓
      n8n Workflow Engine
           ↓
   SMTP Email / Automation
```

---

## 📦 Tech Stack

- Python 3.10+
- Streamlit
- LangChain + LangGraph
- OpenAI GPT-4o-mini
- DuckDuckGo Search
- SQLite (memory)
- n8n (workflow automation)
- SMTP Email

---

## 📁 Project Structure

```
.
├── autonomous.py              # Main AI Agent (Streamlit app)
├── agent.db                   # SQLite database (ignored in git)
├── openaiapikey.py           # API key file (ignored in git)
├── requirements.txt
├── README.md
│
├── n8n/
│   └── workflows/
│       └── write_email_webhook.json
│
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone repo

```bash
git clone https://github.com/your-username/autonomous-ai-agent.git
cd autonomous-ai-agent
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Add OpenAI API key

Create file:

```python
openaiapikey.py
```

Example:

```python
apikey = "your_openai_api_key_here"
```

⚠️ This file is ignored in GitHub (.gitignore)

---

## ▶️ Run the project

```bash
streamlit run autonomous.py
```

---

## 🔌 n8n Workflows

This project includes n8n automation workflows.

### 📂 Location in repo

```
n8n/workflows/write_email_webhook.json
```

---

## 📧 Email Automation Workflow

### Endpoint

```
POST /webhook/write_email
```

### Flow inside n8n

```
Webhook → Send Email (SMTP) → Set Fields → Respond to Webhook
```

### What it does

- Receives request from Python agent
- Extracts text payload
- Sends email via SMTP
- Returns success response

---

## 🧠 How AI + n8n integration works

1. User sends message in Streamlit
2. LangGraph Agent decides:
   - search → DuckDuckGo tool
   - email → trigger_n8n tool
3. Python calls n8n webhook:

```python
trigger_n8n(workflow="email", payload={"text": "Hello"})
```

4. n8n executes workflow
5. Email is sent via SMTP
6. Response is returned to Python

---

## 🔐 Security Notes

- `openaiapikey.py` is NOT pushed to GitHub
- `agent.db` is ignored
- n8n credentials (SMTP, OpenAI) must be configured manually
- Webhook endpoints should be secured in production (recommended: add token auth)

---

## 📌 Example Usage

### Ask AI:

- "Write an email for job interview"
- "Search latest AI trends"
- "Send email about meeting request"

---

## 🧩 n8n Setup Guide

1. Install n8n
2. Import workflow:

```
n8n/workflows/write_email_webhook.json
```

3. Activate workflow
4. Ensure webhook path matches:

```
/write_email
```

---

## 🔥 Future Improvements

- 🔐 Secure webhook authentication (token-based)
- 🧠 Multi-agent system (planner + executor)
- 🗂️ Vector database (RAG memory)
- ⚡ Redis memory layer
- 🐳 Docker deployment
- 🌍 Cloud deployment (Railway / VPS)
- 📊 Admin dashboard
- 🔄 Streaming AI responses

---

## 👨‍💻 Author

Built by **Faramarz Karamizadeh**

- GitHub: https://github.com/f-karamizadeh


---

## 📜 License

MIT License