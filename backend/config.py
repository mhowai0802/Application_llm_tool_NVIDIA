# config.py
MONGO_URI = "mongodb+srv://mhowaiwork:joniwhfe@cluster0.tfwsu.mongodb.net/"
MONGO_DB = "nvidia_reports"
MONGO_COLLECTION = "annual_tocs"
MONGO_COLLECTION_CHART = "nvidia_charts"
MONGO_USER = "mhowaiwork"
MONGO_PASSWORD = "joniwhfe"

MONGO_CONFIG = {
    # MongoDB connection parameters
    'username': 'mhowaiwork',  # Will be set from env vars or user input
    'password': 'joniwhfe',  # Will be set from env vars or user input
    'cluster': 'cluster0.tfwsu.mongodb.net',
    'app_name': 'Cluster0',
    'retry_writes': True,
    'w': 'majority',
    # SSL Configuration
    'ssl': True,
    'ssl_cert_reqs': 'CERT_NONE',  # Can be changed to 'CERT_NONE' to disable verification
    'tls_ca_file': None,  # Path to a CA certificate file if needed
    # Database and collection names
    'database': 'nvidia_reports',
    'collection': 'nvidia_charts'
}

CONFIG = {
    "api": {
        "key": "e7156e27-f44b-4fb1-b34f-fc34a4369b7b",  # Replace with your actual API key
        "base_url": "https://genai.hkbu.edu.hk/general/rest",
        "model": "gpt-4-o-mini",
        "api_version": "2024-05-01-preview"
    },
    "ollama": {
        "model": "llama3.2",
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
        "embedding_model": "nomic-embed-text"  # Ollama embedding model
    },
    "sql_database": {
        "connection_string": "mysql://root:joniwhfe@127.0.0.1/nvidia_db",
        "table_name": "NVIDIA_STOCK"
    },
    "app": {
        "title": "LangChain Chatbot",
        "description": "A chatbot powered by LangChain, Ollama, MongoDB, and SQL"
    }
}