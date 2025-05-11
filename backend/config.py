# config.py
MONGO_URI = "mongodb+srv://mhowaiwork:joniwhfe@cluster0.tfwsu.mongodb.net/"
MONGO_DB = "nvidia_reports"
MONGO_COLLECTION = "annual_tocs"

CONFIG = {
    "api": {
        "key": "e7156e27-f44b-4fb1-b34f-fc34a4369b7b",  # Replace with your actual API key
        "base_url": "https://genai.hkbu.edu.hk/general/rest",
        "model": "gpt-4-o-mini",
        "api_version": "2024-10-21"
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