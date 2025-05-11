from langchain_ollama import OllamaEmbeddings
import config
from config import MONGO_CONFIG
from tools.mongodb_utils import get_mongo_client
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import os
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt
import json
import re

def extract_year(question):
    # Pattern to match 4-digit numbers that could be years (typically 1000-2099)
    year_pattern = r'\b(19\d{2}|20\d{2})\b'

    # Search for the pattern in the question
    match = re.search(year_pattern, question)

    # Return the year if found, otherwise None
    return match.group() if match else None

def connect_to_mongodb(username, password):
    # Get connection parameters from config
    cluster = MONGO_CONFIG['cluster']
    app_name = MONGO_CONFIG['app_name']
    retry_writes = MONGO_CONFIG['retry_writes']
    w_value = MONGO_CONFIG['w']
    connection_timeout = MONGO_CONFIG.get('connection_timeout_ms', 30000)
    selection_timeout = MONGO_CONFIG.get('server_selection_timeout_ms', 30000)
    max_pool_size = MONGO_CONFIG.get('max_pool_size', 100)

    # Create the connection URI
    uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites={'true' if retry_writes else 'false'}&w={w_value}&appName={app_name}"
    uri = "mongodb+srv://mhowaiwork:joniwhfe@cluster0.tfwsu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        # Method 1: Try connecting with certifi (recommended secure method)
        client = MongoClient(
            uri,
            server_api=ServerApi('1'),
            tlsCAFile=certifi.where(),
            connectTimeoutMS=connection_timeout,
            serverSelectionTimeoutMS=selection_timeout,
            maxPoolSize=max_pool_size
        )

        # Test connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

        # Return database handle
        db = client[MONGO_CONFIG['database']]
        return db, client

    except Exception as e:
        print(f"Connection error with certifi: {e}")
        print("Trying fallback connection method...")

        try:
            # Method 2: Try connecting with tlsAllowInvalidCertificates
            client = MongoClient(
                uri,
                server_api=ServerApi('1'),
                tlsAllowInvalidCertificates=True,
                connectTimeoutMS=connection_timeout,
                serverSelectionTimeoutMS=selection_timeout,
                maxPoolSize=max_pool_size
            )

            client.admin.command('ping')
            print("Connected successfully using tlsAllowInvalidCertificates=True")
            db = client[MONGO_CONFIG['database']]
            return db, client

        except Exception as e2:
            print(f"Second connection attempt failed: {e2}")

            try:
                # Method 3: Last resort - try with just the URI
                client = MongoClient(
                    uri,
                    connectTimeoutMS=connection_timeout,
                    serverSelectionTimeoutMS=selection_timeout,
                    maxPoolSize=max_pool_size
                )

                client.admin.command('ping')
                print("Connected successfully using simple connection string")
                db = client[MONGO_CONFIG['database']]
                return db, client

            except Exception as e3:
                print(f"All connection attempts failed. Last error: {e3}")
                raise e3

def retrieve_document_by_name(db, document_name):
    """Retrieve a document by its filename"""
    collection = db[MONGO_CONFIG['collection']]

    # Check if the document name contains an extension
    if '.' not in document_name:
        # Try to find documents that start with the name provided
        cursor = collection.find({'filename': {'$regex': f'^{document_name}', '$options': 'i'}})
        documents = list(cursor)

        if len(documents) == 0:
            print(f"No documents found matching '{document_name}'")
            return None
        elif len(documents) > 1:
            print(f"Multiple documents found matching '{document_name}':")
            for i, doc in enumerate(documents):
                print(f"{i + 1}. {doc['filename']}")
            selection = input("Enter the number of the document to retrieve: ")
            try:
                index = int(selection) - 1
                if 0 <= index < len(documents):
                    return documents[index]
                else:
                    print("Invalid selection.")
                    return None
            except ValueError:
                print("Please enter a valid number.")
                return None
        else:
            return documents[0]
    else:
        # Try exact match first
        document = collection.find_one({'filename': document_name})

        if not document:
            # If exact match fails, try case-insensitive search
            document = collection.find_one({'filename': {'$regex': f'^{document_name}$', '$options': 'i'}})

        if not document:
            print(f"Document with name '{document_name}' not found.")
            return None

        return document

def extract_all_charts(db, document_name, output_dir=None):
    """Extract all charts from a document by name and save them to the output directory"""
    # If no output_dir specified, create one based on document name
    if not output_dir:
        base_name = os.path.splitext(document_name)[0] if '.' in document_name else document_name
        output_dir = f"charts_{base_name}"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Retrieve the document
    document = retrieve_document_by_name(db, document_name)

    if not document:
        return False

    print(f"Retrieved document: {document['filename']}")

    # Get charts from document
    sections = document.get('sections', {})
    charts = sections.get('charts', {})

    if not charts:
        print(f"No charts found in document '{document['filename']}'")
        return False

    print(f"Found {len(charts)} charts in document '{document['filename']}'")
    print(f"Saving charts to directory: {output_dir}")

    saved_files = []
    for category, chart_data in charts.items():
        if 'chart_data' in chart_data:
            try:
                # Decode base64 image
                img_bytes = base64.b64decode(chart_data['chart_data'])
                img = Image.open(io.BytesIO(img_bytes))

                # Save image
                filename = f"{category}_chart.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath)
                print(f"Saved: {filepath}")
                saved_files.append(filepath)
            except Exception as e:
                print(f"Error saving chart for {category}: {e}")
        else:
            print(f"No chart data found for {category}")

    print(f"Successfully saved {len(saved_files)} charts to {output_dir}")
    return len(saved_files) > 0


def get_chart_data(document_name):
    """Get chart data without saving to disk - for direct display in Streamlit"""
    mongo_username = config.MONGO_USER
    mongo_password = config.MONGO_PASSWORD

    try:
        db, client = connect_to_mongodb(mongo_username, mongo_password)

        # Retrieve the document
        document = retrieve_document_by_name(db, document_name)

        if not document:
            client.close()
            return None

        # Get charts from document
        sections = document.get('sections', {})
        charts = sections.get('charts', {})

        if not charts:
            print(f"No charts found in document '{document['filename']}'")
            client.close()
            return None

        # Prepare chart data for return (keep base64 format for direct display)
        chart_results = {
            'document_name': document['filename'],
            'charts': {}
        }

        for category, chart_data in charts.items():
            if 'chart_data' in chart_data:
                # Store the base64 data directly
                chart_results['charts'][category] = {
                    'title': category.replace('_', ' ').title(),
                    'image_data': chart_data['chart_data']
                }

        client.close()
        return chart_results

    except Exception as e:
        print(f"Error retrieving chart data: {e}")
        if 'client' in locals():
            client.close()
        return None


def retrieve_chart(query: str):
    """Find and return chart data based on semantic query"""
    client = get_mongo_client()
    db = client[config.MONGO_DB]
    collection = db[config.MONGO_COLLECTION_CHART]
    embeddings = OllamaEmbeddings(
        base_url=config.CONFIG["ollama"]["base_url"],
        model=config.CONFIG["ollama"]["embedding_model"]
    )

    # First similarity search to find the most relevant document by filename
    docs_by_filename = collection.find({}, {"filename": 1, "_id": 1})

    year = extract_year(query)

    # Use Ollama embeddings for the query
    query_embedding = embeddings.embed_query(year)
    best_doc = None
    best_score = -1

    for doc in docs_by_filename:
        filename_embedding = embeddings.embed_query(doc["filename"])
        # Calculate similarity (dot product)
        similarity = sum(a * b for a, b in zip(query_embedding, filename_embedding))
        if similarity > best_score:
            best_score = similarity
            best_doc = doc

    if not best_doc:
        print("No matching document found")
        return None

    print(f"Best matching document: {best_doc['filename']}")
    # Get the chart data
    chart_data = get_chart_data(best_doc['filename'])

    return chart_data