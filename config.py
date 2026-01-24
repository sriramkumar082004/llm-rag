# Crime Dataset Configuration
CSV_FILE = "crime.csv"

# Columns to include in the combined text for embeddings
CRIME_COLUMNS = {
    "dr_no": "DR_NO",
    "crime_desc": "Crm Cd Desc",
    "location": "LOCATION",
    "area_name": "AREA NAME",
    "date_occ": "DATE OCC",
    "time_occ": "TIME OCC",
    "vict_age": "Vict Age",
    "vict_sex": "Vict Sex",
    "premis_desc": "Premis Desc",
    "status_desc": "Status Desc",
    "weapon_desc": "Weapon Desc",
    "lat": "LAT",
    "lon": "LON",
}

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"

# FAISS Index
INDEX_FILE = "crime_index.faiss"

# Redis Cache TTL (in seconds)
CACHE_TTL = 1800  # 30 minutes
