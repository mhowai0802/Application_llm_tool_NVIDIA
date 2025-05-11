import PyPDF2
import tabula
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re
import numpy as np
import os
import certifi
import glob
from tqdm import tqdm

# Import configuration
from pdf_extraction_chart_table.config import MONGO_CONFIG, PDF_CONFIG


def connect_to_mongodb():
    """Connect to MongoDB using credentials from config."""
    username = MONGO_CONFIG['username']
    password = MONGO_CONFIG['password']
    cluster = MONGO_CONFIG['cluster']
    app_name = MONGO_CONFIG['app_name']
    retry_writes = MONGO_CONFIG['retry_writes']
    w_value = MONGO_CONFIG['w']

    # Create connection URI
    uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites={'true' if retry_writes else 'false'}&w={w_value}&appName={app_name}"

    try:
        # Connect with certifi
        client = MongoClient(
            uri,
            server_api=ServerApi('1'),
            tlsCAFile=certifi.where()
        )

        # Test connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        return client[MONGO_CONFIG['database']]

    except Exception as e:
        print(f"Connection error: {e}")

        try:
            # Fallback connection
            client = MongoClient(uri)
            client.admin.command('ping')
            print("Connected using fallback method")
            return client[MONGO_CONFIG['database']]
        except Exception as e2:
            print(f"All connection attempts failed: {e2}")
            raise e2


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return "".join(page.extract_text() for page in reader.pages)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF using tabula."""
    try:
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

        processed_tables = []
        for i, table in enumerate(tables):
            if not table.empty:
                table.columns = [str(col).strip() for col in table.columns]
                processed_tables.append({
                    'table_id': i,
                    'data': table.to_dict(orient='records'),
                    'columns': table.columns.tolist()
                })

        return processed_tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []


def extract_financial_data(pdf_text):
    """Extract financial data using regex patterns."""
    patterns = PDF_CONFIG['patterns']

    financial_data = {
        'revenue': [],
        'data_center': [],
        'gaming': [],
        'professional_viz': [],
        'automotive': [],
        'cash_flow': [],
        'quarters': [],
        'financial_summary': []
    }

    # Extract data for each section
    sections = [
        ('financial_summary', 'financial_summary'),
        ('data_center', 'data_center'),
        ('gaming', 'gaming'),
        ('pro_viz', 'professional_viz'),
        ('auto', 'automotive'),
        ('cash_flow', 'cash_flow')
    ]
    print(pdf_text)
    for section_key, data_key in sections:
        pattern = patterns.get(section_key)
        if not pattern:
            continue

        matches = re.findall(pattern, pdf_text, re.DOTALL)
        print(pattern)
        print(matches)
        if matches:
            values = re.findall(patterns['quarterly'], matches[0])
            financial_data[data_key] = [int(v.replace(',', '')) for v in values]

    # Extract quarterly labels
    quarters = re.findall(patterns['quarters'], pdf_text)
    unique_quarters = []
    for q in quarters:
        if q not in unique_quarters:
            unique_quarters.append(q)

    financial_data['quarters'] = unique_quarters[:5]  # Assuming 5 quarters
    return financial_data


def extract_financial_summary(pdf_text):
    """Extract the financial summary table."""
    summary_pattern = PDF_CONFIG['patterns']['financial_summary']
    match = re.search(summary_pattern, pdf_text, re.DOTALL)

    if not match:
        return None

    summary_text = match.group(1)

    # Extract GAAP and Non-GAAP data
    metrics = ['Revenue', 'Gross Margin', 'Operating Income', 'Net Income', 'Diluted EPS', 'Cash Flow from Ops']
    summary_data = {
        'GAAP': {},
        'Non-GAAP': {}
    }

    for metric in metrics:
        gaap_pattern = rf'{metric}\s+\$([\d,]+)\s+\+(\d+)%\s+\+(\d+)%'
        non_gaap_pattern = rf'\$([\d,]+)\s+\+(\d+)%\s+\+(\d+)%'

        gaap_match = re.search(gaap_pattern, summary_text)
        if not gaap_match:
            continue

        # Process GAAP data
        value = gaap_match.group(1).replace(',', '')
        yoy = gaap_match.group(2)
        qoq = gaap_match.group(3)

        summary_data['GAAP'][metric] = {
            'value': int(value) if value.isdigit() else value,
            'yoy': f"+{yoy}%",
            'qoq': f"+{qoq}%"
        }

        # Find Non-GAAP data
        rest_of_text = summary_text[summary_text.find(gaap_match.group(0)) + len(gaap_match.group(0)):]
        non_gaap_match = re.search(non_gaap_pattern, rest_of_text)

        if non_gaap_match:
            value = non_gaap_match.group(1).replace(',', '')
            yoy = non_gaap_match.group(2)
            qoq = non_gaap_match.group(3)

            summary_data['Non-GAAP'][metric] = {
                'value': int(value) if value.isdigit() else value,
                'yoy': f"+{yoy}%",
                'qoq': f"+{qoq}%"
            }

    return summary_data


def create_charts(financial_data):
    """Create charts from the financial data."""
    if not financial_data:
        return {}

    charts = {}

    # Get configuration settings
    chart_width = PDF_CONFIG['chart_width']
    chart_height = PDF_CONFIG['chart_height']
    chart_dpi = PDF_CONFIG['chart_dpi']
    categories = PDF_CONFIG['categories']

    # Get quarters
    quarters = financial_data.get('quarters', [])
    if not quarters:
        return {}

    # Create individual charts
    for category in categories:
        if category in financial_data and financial_data[category]:
            data_points = financial_data[category]
            if len(data_points) > len(quarters):
                data_points = data_points[:len(quarters)]

            display_quarters = quarters[:len(data_points)]

            if display_quarters:
                plt.figure(figsize=(chart_width, chart_height))
                plt.bar(display_quarters, data_points)
                plt.title(f'{category.replace("_", " ").title()} Revenue')
                plt.ylabel('Revenue ($M)')
                plt.xlabel('Quarter')
                plt.xticks(rotation=45)
                plt.grid(axis='y', linestyle='--', alpha=0.7)

                # Add value labels
                for i, v in enumerate(data_points):
                    plt.text(i, v + (max(data_points) * 0.02), f"${v:,}",
                             ha='center', va='bottom', fontweight='bold')

                plt.tight_layout()

                # Save chart to buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=chart_dpi)
                buffer.seek(0)

                # Convert to base64
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()

                charts[category] = {
                    'chart_data': img_str,
                    'values': data_points,
                    'quarters': display_quarters
                }

    return charts


def process_pdf(pdf_path, db):
    """Process a single PDF file and store in MongoDB."""
    try:
        # Get filename
        filename = os.path.basename(pdf_path)

        # Check if file already exists in database
        collection = db[MONGO_CONFIG['collection']]
        existing = collection.find_one({"filename": filename})

        # Extract text
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print(f"Could not extract text from {filename}, skipping")
            return False

        # Create document
        document = {
            "filename": filename,
            "sections": {},
            "processed_date": pd.Timestamp.now().isoformat()
        }

        # Extract data based on configuration
        if PDF_CONFIG['extract_tables']:
            document["sections"]["tables"] = extract_tables_from_pdf(pdf_path)

        if PDF_CONFIG['extract_financial_data']:
            document["sections"]["financial_data"] = extract_financial_data(pdf_text)

        if PDF_CONFIG['extract_financial_summary']:
            document["sections"]["financial_summary"] = extract_financial_summary(pdf_text)

        if PDF_CONFIG['create_visualizations'] and 'financial_data' in document["sections"]:
            document["sections"]["charts"] = create_charts(document["sections"]["financial_data"])

        # Store or update in MongoDB
        if existing:
            collection.update_one(
                {'_id': existing['_id']},
                {'$set': document}
            )
        else:
            collection.insert_one(document)

        return True

    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {e}")
        return False


def process_directory(pdf_directory):
    """Process all PDF files in a directory."""
    # Check if directory exists
    if not os.path.isdir(pdf_directory):
        print(f"Directory not found: {pdf_directory}")
        return

    # Find PDF files
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        return

    print(f"Found {len(pdf_files)} PDF files in {pdf_directory}")

    # Connect to MongoDB
    db = connect_to_mongodb()

    # Process each file
    success_count = 0
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        if process_pdf(pdf_file, db):
            success_count += 1
        break

    print(f"Successfully processed {success_count} out of {len(pdf_files)} PDF files")


if __name__ == "__main__":
    # Get directory path from argument or input
    pdf_directory = PDF_CONFIG['pdf_dir']

    process_directory(pdf_directory)
