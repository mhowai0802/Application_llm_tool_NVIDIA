import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# load .env
load_dotenv(find_dotenv())

# MongoDB
MONGO_URI        = os.getenv("MONGO_URI")
MONGO_DB         = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# PDF & JSON
REPORTS_DIR     = Path(os.getenv("REPORTS_DIR", "annual_report"))
JSON_OUTPUT     = Path(os.getenv("JSON_OUTPUT", "output.json"))
_raw_sections   = os.getenv("SECTION_NAMES", "")
SECTION_NAMES   = [s.strip() for s in _raw_sections.split(",") if s.strip()] or None

# Retrieval params
TOP_K_FILENAMES          = int(os.getenv("TOP_K_FILENAMES", 5))
TOP_K_SECTION_CANDIDATES = int(os.getenv("TOP_K_SECTION_CANDIDATES", 7))
REFINE_TOP_N_SECTIONS    = int(os.getenv("REFINE_TOP_N_SECTIONS", 3))

# HKBU Chat Completion API
CHATGPT_BASICURL     = os.getenv("CHATGPT_BASICURL")
CHATGPT_MODELNAME    = os.getenv("CHATGPT_MODELNAME")
CHATGPT_APIVERSION   = os.getenv("CHATGPT_APIVERSION")
CHATGPT_ACCESS_TOKEN = os.getenv("CHATGPT_ACCESS_TOKEN")

# Ollama embedding
OLLAMA_EMBED_MODELNAME = os.getenv("OLLAMA_EMBED_MODELNAME")