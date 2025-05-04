# mongodb_tool.py
# Update the import at the top
from langchain.tools import tool
from langchain_ollama import OllamaEmbeddings
from tools.mongodb_utils import get_mongo_client
import config
import re


def extract_year(question):
    # Pattern to match 4-digit numbers that could be years (typically 1000-2099)
    year_pattern = r'\b(19\d{2}|20\d{2})\b'

    # Search for the pattern in the question
    match = re.search(year_pattern, question)

    # Return the year if found, otherwise None
    return match.group() if match else None

@tool
def retrieve_from_mongodb(query: str) -> str:
    """Retrieves information from MongoDB based on similarity search."""
    client = get_mongo_client()
    try:
        db = client[config.MONGO_DB]
        collection = db[config.MONGO_COLLECTION]
        embeddings = OllamaEmbeddings(
            base_url=config.CONFIG["ollama"]["base_url"],
            model=config.CONFIG["ollama"]["embedding_model"]
        )

        # First similarity search to find the most relevant document by filename
        docs_by_filename = collection.find({}, {"filename": 1, "_id": 1})
        # Use Ollama embeddings for the query

        year = extract_year(query)
        query_embedding = embeddings.embed_query(year)

        # Find most similar document based on filename
        best_doc = None
        best_score = -1

        for doc in docs_by_filename:
            print(doc["filename"])
            filename_embedding = embeddings.embed_query(doc["filename"])

            # Calculate similarity (dot product)
            similarity = sum(a * b for a, b in zip(query_embedding, filename_embedding))
            print(similarity)
            if similarity > best_score:
                best_score = similarity
                best_doc = doc

        if not best_doc:
            return "No relevant documents found."

        # Now retrieve the document and its sections
        full_doc = collection.find_one({"_id": best_doc["_id"]})
        if not full_doc or "sections" not in full_doc:
            return f"Found document {best_doc['filename']} but it has no sections."

        # Find top 3 most similar sections
        sections = full_doc["sections"]
        section_similarities = []

        for key, content in sections.items():
            section_embedding = embeddings.embed_query(key)
            similarity = sum(a * b for a, b in zip(query_embedding, section_embedding))
            section_similarities.append((key, content, similarity))

        # Sort by similarity score and take top 3
        section_similarities.sort(key=lambda x: x[2], reverse=True)
        top_sections = section_similarities[:3]

        # Format the result
        result = f"Information from document: {full_doc['filename']}\n\n"

        for key, content, _ in top_sections:
            result += f"Section: {key}\n{content}\n\n"

        return result
    finally:
        client.close()