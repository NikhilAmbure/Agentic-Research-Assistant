# 🔍 Agentic Research Assistant

An AI-powered research assistant built with **Django** and **LangGraph** that autonomously searches the web, synthesizes information, and delivers well-structured research responses through a conversational chat interface.

---

## 🚀 Features

- **Agentic Research Loop** — Uses LangGraph to orchestrate a stateful research workflow that can plan, search, and iterate.
- **Multi-Provider LLM Support** — Integrates with Google Gemini (`langchain-google-genai`) and Groq (`langchain-groq`) for flexible model selection.
- **Web Search Tools** — Leverages Tavily (`langchain-tavily`) and DuckDuckGo (`duckduckgo-search`) for real-time web lookups.
- **Conversational Chat Interface** — Django-powered `chat` app provides a persistent, history-aware conversation experience.
- **REST API Backend** — Clean Django REST endpoints with CORS support for frontend integration.
- **SQLite Storage** — Lightweight persistent storage for conversation history out of the box.

---

## 🏗️ Project Structure

```
Agentic-Research-Assistant/
├── Agentic_Research_Assistant/   # Django project settings & URL config
├── agent/                        # LangGraph agent logic & API views
├── chat/                         # Chat session management app
├── manage.py                     # Django management CLI
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # SQLite database
└── .gitignore
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Django 5.1.4 |
| Agent Orchestration | LangGraph |
| LLM Integrations | Google Gemini, Groq |
| Search Tools | Tavily, DuckDuckGo |
| LLM Framework | LangChain (Core, Community) |
| CORS | django-cors-headers |
| Config | python-dotenv |
| Validation | Pydantic v2 |
| Database | SQLite |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10+
- API keys for your chosen LLM provider (Google Gemini and/or Groq)
- Tavily API key (optional, for enhanced search)

### 1. Clone the Repository

```bash
git clone https://github.com/NikhilAmbure/Agentic-Research-Assistant.git
cd Agentic-Research-Assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM Providers (add whichever you use)
GOOGLE_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# Search Tools
TAVILY_API_KEY=your_tavily_api_key

# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

## 🔌 API Usage

### Send a Research Query

```http
POST /agent/query/
Content-Type: application/json

{
  "query": "What are the latest breakthroughs in quantum computing?"
}
```

### Chat Endpoint

```http
POST /chat/message/
Content-Type: application/json

{
  "session_id": "abc123",
  "message": "Summarize the key trends in renewable energy in 2025"
}
```

---

## 🧠 How It Works

1. **User Query** — The user submits a research question via the chat or agent API.
2. **LangGraph Orchestration** — The agent graph plans the research steps, deciding when to search, when to synthesize, and when to return a final answer.
3. **Tool Invocation** — The agent calls Tavily or DuckDuckGo to fetch real-time web results.
4. **LLM Synthesis** — Retrieved information is processed by Google Gemini or Groq to produce a coherent, cited response.
5. **Response Delivery** — The final answer is streamed/returned through the Django REST API.

---

## 📦 Dependencies

```
django==5.1.4
django-cors-headers==4.6.0
python-dotenv==1.0.1
pydantic==2.10.3
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langchain-google-genai
langchain-groq
langchain-tavily
langgraph
duckduckgo-search==6.3.7
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. Please check the repository for license details.

---

## 👤 Author

**Nikhil Ambure** — [GitHub](https://github.com/NikhilAmbure)