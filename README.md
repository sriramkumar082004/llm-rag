# LLM-RAG Hybrid AI System

A production-level **Hybrid RAG (Retrieval-Augmented Generation)** system that intelligently routes queries to the most appropriate data source using a four-way classification system. Built with FastAPI, PostgreSQL, FAISS vector store, Ollama (Phi-3), and Redis caching.

## 🌟 Features

### Intelligent Query Routing

The system automatically classifies and routes queries to one of four specialized data sources:

- **🎓 Student Data** → PostgreSQL database queries
- **🌐 Live/Current Data** → DuckDuckGo web search
- **🔍 Domain-Specific Data** → RAG on crime database (FAISS + embeddings)
- **🤖 General Knowledge** → Direct Ollama LLM queries

### Performance Optimization

- **Redis Caching** with adaptive TTL (Time-To-Live) based on data source
- **Connection Pooling** for efficient database access
- **Batch Processing** for vector embeddings

### Advanced Capabilities

- Natural language processing for database queries
- Semantic search using sentence transformers
- Context-aware responses with source attribution
- Real-time web search integration

## 📁 Project Structure

```
llm-rag/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
│
├── mcp/                        # Multi-Component Pipeline
│   ├── __init__.py
│   ├── intent_classifier.py   # Intent classification logic
│   └── tool_router.py          # Query routing system
│
├── tools/                      # External data source integrations
│   ├── __init__.py
│   ├── student_api.py          # PostgreSQL student data API
│   └── duckduckgo_search.py    # Web search integration
│
├── db.py                       # Database connection & pooling
├── rag.py                      # RAG core logic (vector search + LLM)
├── vector_store.py             # FAISS vector store operations
├── build_index.py              # Index builder for embeddings
├── embeddings.py               # Embedding generation utilities
├── redis_cache.py              # Redis caching layer
│
├── crime.csv                   # Crime dataset (Los Angeles)
├── crime_index.faiss           # FAISS index file
└── crime_texts.pkl             # Preprocessed text data
```

## 🛠️ Tech Stack

| Component               | Technology                                 |
| ----------------------- | ------------------------------------------ |
| **Backend Framework**   | FastAPI                                    |
| **LLM**                 | Ollama (Phi-3 model)                       |
| **Vector Database**     | FAISS                                      |
| **Relational Database** | PostgreSQL                                 |
| **Caching**             | Redis                                      |
| **Embeddings**          | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Web Search**          | DuckDuckGo API                             |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (with student data)
- Redis server
- Ollama installed with Phi-3 model

### Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd llm-rag
```

2. **Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
DB_HOST=your-db-host.com
DB_NAME=student_db_qoou
DB_USER=your-username
DB_PASSWORD=your-password
DB_PORT=5432
```

5. **Build the FAISS index**

```bash
python build_index.py
```

6. **Start Redis** (if not already running)

```bash
redis-server
```

7. **Start Ollama with Phi-3**

```bash
ollama run phi3
```

8. **Run the application**

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Main Endpoint: `/ask`

**Description:** Intelligent query endpoint that automatically routes questions to the appropriate data source.

**Method:** `GET`

**Parameters:**

- `question` (string, required): The natural language question

**Response:**

```json
{
  "source": "student|web|rag|general",
  "answer": "The generated answer",
  "cached": true|false
}
```

### Examples

#### Query Student Data

```bash
curl "http://localhost:8000/ask?question=How%20many%20students%20are%20there?"
```

Response:

```json
{
  "source": "student",
  "answer": "There are 150 students in the database.",
  "cached": false
}
```

#### Query Crime Data (RAG)

```bash
curl "http://localhost:8000/ask?question=What%20are%20the%20most%20common%20crimes%20in%20Los%20Angeles?"
```

Response:

```json
{
  "source": "rag",
  "answer": "Based on the crime records, the most common crimes are...",
  "cached": false
}
```

#### Live Web Search

```bash
curl "http://localhost:8000/ask?question=What%20is%20the%20weather%20today?"
```

Response:

```json
{
  "source": "web",
  "answer": "Current weather information...",
  "cached": false
}
```

#### General Knowledge

```bash
curl "http://localhost:8000/ask?question=What%20is%20the%20capital%20of%20France?"
```

Response:

```json
{
  "source": "general",
  "answer": "The capital of France is Paris.",
  "cached": false
}
```

## 🔧 Configuration

### Cache TTL Settings

The system uses adaptive caching based on data source:

| Source      | TTL            | Description                     |
| ----------- | -------------- | ------------------------------- |
| **student** | 10 min (600s)  | Student data changes moderately |
| **web**     | 5 min (300s)   | Live data changes frequently    |
| **rag**     | 30 min (1800s) | Crime data is relatively static |
| **general** | 15 min (900s)  | General knowledge is stable     |

### Ollama Configuration

Edit `config.py` to change the LLM settings:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"  # or any other Ollama model
```

### Embedding Model

The system uses `all-MiniLM-L6-v2` for generating embeddings. To change:

```python
EMBEDDING_MODEL = "your-preferred-model"
```

## 🧠 How It Works

### 1. Intent Classification

When a query arrives, the `intent_classifier.py` analyzes it to determine the intent:

- **Student-related** keywords: "student", "course", "enrollment", etc.
- **Live data** indicators: "today", "current", "latest", "now", etc.
- **Crime-related** keywords: "crime", "police", "arrest", "theft", etc.
- **Default**: General knowledge

### 2. Query Routing

Based on the classified intent, the `tool_router.py` routes to:

```
┌─────────────┐
│   Question  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Intent Classifier│
└──────┬───────────┘
       │
       ├──► Student  ──► PostgreSQL Database
       │
       ├──► Web      ──► DuckDuckGo Search
       │
       ├──► RAG      ──► FAISS Vector Search + Ollama
       │
       └──► General  ──► Direct Ollama Query
```

### 3. RAG Pipeline

For domain-specific queries (crime data):

1. **Query Embedding**: Convert question to vector using sentence transformers
2. **Similarity Search**: Find top-K similar records in FAISS index
3. **Context Retrieval**: Fetch relevant crime records
4. **LLM Generation**: Send context + question to Ollama
5. **Response**: Return generated answer with source attribution

### 4. Caching Layer

Redis caches responses to reduce latency and API costs:

```python
# Cache hit → Return immediately
# Cache miss → Process query → Store in cache
```

## 🧪 Testing

### Test Database Connection

```bash
python db.py
```

### Test Individual Components

**Test RAG system:**

```python
from rag import rag_answer
answer = rag_answer("What crimes happened in downtown LA?")
print(answer)
```

**Test web search:**

```python
from tools.duckduckgo_search import live_search
results = live_search("latest AI news", max_results=5)
print(results)
```

**Test student queries:**

```python
from tools.student_api import query_students_natural
answer = query_students_natural("How many CS students are there?")
print(answer)
```

## 📊 Dataset

The project uses the **Los Angeles Crime Dataset** (`crime.csv`) with the following fields:

- DR_NO (Report Number)
- Crime Description
- Location
- Area Name
- Date/Time of Occurrence
- Victim Demographics
- Premise Description
- Status
- Weapon Description
- Coordinates (LAT/LON)

## 🔒 Security Notes

- Store sensitive credentials in `.env` file (never commit to Git)
- Use environment variables for all database connections
- Implement rate limiting for production deployments
- Use connection pooling to prevent resource exhaustion

## 🚧 Future Enhancements

- [ ] Add authentication & authorization
- [ ] Implement query logging and analytics
- [ ] Add more data sources (APIs, databases)
- [ ] Implement streaming responses
- [ ] Add support for multiple languages
- [ ] Build a web UI dashboard
- [ ] Implement A/B testing for routing algorithms
- [ ] Add support for document uploads

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM infrastructure
- **FastAPI** for the excellent web framework
- **FAISS** by Facebook AI Research for efficient similarity search
- **Sentence Transformers** for high-quality embeddings
- **DuckDuckGo** for privacy-respecting search API

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Python, FastAPI, and AI**
