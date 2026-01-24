# Crime RAG System

A Retrieval-Augmented Generation (RAG) system for querying Los Angeles crime data using FAISS vector search, sentence embeddings, and Ollama LLM.

## Dataset Schema

The system works with crime data CSV files containing the following columns:

- **DR_NO**: Division of Records Number (unique identifier)
- **Date Rptd**: Date the crime was reported
- **DATE OCC**: Date the crime occurred
- **TIME OCC**: Time the crime occurred
- **AREA**: Geographic area code
- **AREA NAME**: Name of the geographic area
- **Crm Cd**: Crime code
- **Crm Cd Desc**: Crime description
- **Vict Age**: Victim's age
- **Vict Sex**: Victim's sex
- **Vict Descent**: Victim's descent/ethnicity
- **Premis Cd**: Premises code
- **Premis Desc**: Premises description
- **Weapon Used Cd**: Weapon code
- **Weapon Desc**: Weapon description
- **Status**: Investigation status code
- **Status Desc**: Investigation status description
- **LOCATION**: Street address
- **LAT, LON**: Geographic coordinates

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment (if using venv)
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 2. Ensure Ollama is Running

Make sure Ollama is installed and running with the phi3 model:

```bash
ollama serve
ollama pull phi3
```

### 3. Ensure Redis is Running

Install and start Redis server on port 6379 (default).

### 4. Build the Vector Index

**IMPORTANT**: Run this before starting the API server:

```bash
python build_index.py
```

This will:

- Read the `crime.csv` file
- Generate embeddings for all crime records
- Build a FAISS vector index
- Save the index to `crime_index.faiss`
- Save the text data to `crime_texts.pkl`

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage

### Query the API

```bash
# Example: Ask about crimes in a specific area
curl "http://localhost:8000/ask?question=What crimes happened in Hollywood?"

# Example: Ask about specific crime types
curl "http://localhost:8000/ask?question=Tell me about theft cases"

# Example: Ask about victim demographics
curl "http://localhost:8000/ask?question=What are the age ranges of victims?"
```

### Response Format

```json
{
  "source": "redis-cache" | "rag-faiss-ollama",
  "answer": "The answer from the LLM based on crime records..."
}
```

## Architecture

1. **Vector Store (`vector_store.py`)**: Loads pre-built FAISS index and performs similarity search
2. **Embeddings (`embeddings.py`)**: Generates sentence embeddings using SentenceTransformers
3. **RAG Pipeline (`rag.py`)**: Retrieves relevant records and generates answers using Ollama
4. **Redis Cache (`redis_cache.py`)**: Caches responses to reduce latency
5. **API (`main.py`)**: FastAPI endpoint for querying

## Configuration

Edit `config.py` to customize:

- CSV file path
- Column mappings
- Embedding model
- Ollama URL and model name
- Cache TTL

## Rebuilding the Index

If you update the CSV file or change the column mappings, rebuild the index:

```bash
python build_index.py
```

## Files Generated

- `crime_index.faiss`: FAISS vector index
- `crime_texts.pkl`: Pickled text data for retrieval
