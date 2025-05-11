# MongoDB Atlas Configuration
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
# PDF Processing Configuration
PDF_CONFIG = {
    # Default PDF path
    'pdf_path': 'pdf_extraction_chart_table/NVDA-F4Q25-Quarterly-Presentation-FINAL.pdf',
    'pdf_dir': '/Users/waiwai/Desktop/Github/Application_llm_tool_NVIDIA/pdf_extraction_chart_table/input_files',
    # Extraction settings
    'extract_tables': True,
    'extract_financial_data': True,
    'extract_financial_summary': True,
    'create_visualizations': True,

    # Visualization settings
    'chart_dpi': 300,
    'chart_width': 10,
    'chart_height': 6,
    'combined_chart_width': 12,
    'combined_chart_height': 8,

    # Regular expression patterns for data extraction
    'patterns': {
        'data_center': r'Data Center\nRevenue \(\$M\)(.*?)(?=Highlights|$)',
        'gaming': r'Gaming\nRevenue \(\$M\)(.*?)(?=Highlights|$)',
        'pro_viz': r'Professional Visualization\nRevenue \(\$M\)(.*?)(?=Highlights|$)',
        'auto': r'Automotive\nRevenue \(\$M\)(.*?)(?=Highlights|$)',
        'cash_flow': r'Cash Flow from Operations \(\$M\)(.*?)(?=Highlights|$)',
        'quarterly': r'\$([0-9,]+)',
        'quarters': r'(Q\d FY\d\d)',
        'financial_summary': r'from Ops.*?%$(.*?)Highlights'
    },

    # Categories to extract and visualize
    'categories': ['data_center', 'gaming', 'professional_viz', 'automotive', 'cash_flow','financial_summary'],
    'combined_categories': ['data_center', 'gaming', 'professional_viz', 'automotive']
}