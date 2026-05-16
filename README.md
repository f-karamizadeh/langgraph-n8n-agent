# 🤖 Autonomous AI Agent (LangGraph + n8n)

A lightweight **Autonomous AI Agent** built with **LangGraph, LangChain, Streamlit, OpenAI, and n8n**.

This agent can:
- 🧠 Decide and use tools automatically
- 📧 Generate formal emails via n8n webhook
- 🌐 Perform real-time web search
- 💾 Store conversation history in SQLite
- 🧩 Run fully autonomous workflows

---

## 🚀 Features

- Fully autonomous tool-using AI agent
- LangGraph ReAct-based reasoning
- Web search via DuckDuckGo
- n8n automation integration (webhooks)
- Persistent chat memory (SQLite)
- Simple Streamlit UI
- No external backend required

---

## 🧱 Architecture

```
User → Streamlit UI → Autonomous Agent (LangGraph)
                          │
                          ├── real_search (DuckDuckGo)
                          ├── trigger_n8n (Automation)
                          └── SQLite Memory
                                   ↓
                            Persistent Chat History
```

---

## 📦 Tech Stack

- Python 3.10+
- Streamlit
- LangChain
- LangGraph
- OpenAI GPT-4o-mini
- DuckDuckGo Search
- SQLite
- n8n (workflow automation)

---

## ⚙️ Installation

### 1. Clone repository

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

### 3. OpenAI API Key Setup

This project uses a local file for the API key.

Create file:

```
openaiapikey.py
```

Example:

```python
apikey = "your_openai_api_key_here"
```

⚠️ This file is NOT pushed to GitHub (already ignored in .gitignore)

---

## ▶️ Run the app

```bash
streamlit run autonomous.py
```

---

## 🔌 n8n Integration

This agent can trigger external workflows via n8n.

### Example webhook:

```
http://localhost:5678/webhook/write_email
```

### Supported workflows:

| Workflow | Description |
|----------|------------|
| email    | Generates and sends email via n8n |

---

## 🧠 How it works

1. User sends a message in Streamlit
2. LangGraph agent decides:
   - search → real_search
   - email → trigger_n8n
3. Tool is executed
4. Result stored in SQLite
5. Response returned to UI

---

## 💾 Database

All conversations are stored locally:

```
agent.db
```

Table structure:

- id
- thread_id
- role
- content
- created_at

---

## 🔒 Security Notes

- `openaiapikey.py` is excluded from GitHub
- Never expose API keys publicly
- SQLite DB is local only
- n8n webhook URLs should be secured in production

---

## 📁 Project Structure

```
.
├── autonomous.py          # Main Streamlit App
├── agent.db               # SQLite database (ignored in git)
├── openaiapikey.py        # API key file (ignored in git)
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🧩 Future Improvements

- 🔄 Streaming responses (token-by-token)
- 🧠 Multi-agent system (planner + executor)
- 🗂️ Vector database (RAG memory)
- ⚡ Redis memory layer
- 🐳 Docker deployment
- 🌍 Deploy to cloud (Railway / Render / VPS)
- 🔐 Authentication system
- 📊 Analytics dashboard

---

## 👨‍💻 Author

Built by **Your Name**

- GitHub: https://github.com/your-username
- LinkedIn: https://linkedin.com/in/your-profile

---

## 📜 License

MIT License