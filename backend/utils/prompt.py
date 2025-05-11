from langchain.prompts import PromptTemplate

# Router prompt - more concise with clearer decision criteria
ROUTER_TEMPLATE = """
Determine which tool to use for this NVIDIA question.

TOOLS:
1. MongoDB Retriever: For NVIDIA annual reports, company information, business strategy, products, or history, proxy statement
2. SQL Generator: For NVIDIA stock prices, performance metrics, or market trends
3. Charts Retriever: For NVIDIA quarter reports, there are charts about financial information

User Question: {question}

RESPONSE (ONLY 'mongodb' OR 'sql' - NO OTHER TEXT):
"""

ROUTER_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=ROUTER_TEMPLATE
)

# Simplified general fallback prompt
GENERAL_TEMPLATE = """
User question about NVIDIA: {question}

Provide a concise, informative response focusing only on known NVIDIA information.
"""

GENERAL_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=GENERAL_TEMPLATE
)

# More focused enhancement prompt
ENHANCEMENT_TEMPLATE = """
Question: {question}

Raw data: {raw_response}

Convert this raw data into a concise response that:
- Directly answers the question
- Highlights 2-3 key points with specific figures
- Acknowledges any information gaps
- Uses professional language
"""

ENHANCEMENT_PROMPT = PromptTemplate(
    input_variables=["question", "raw_response"],
    template=ENHANCEMENT_TEMPLATE
)

# MongoDB enhancement with clearer structure
MONGODB_ENHANCEMENT_TEMPLATE = """
Question about NVIDIA's business: {question}

Annual report data: {raw_response}

Provide a response that in point form (maximum 5 points):
- Answers the core question with figures in each point
- Structures information in logical order of importance
- Maintains professional financial reporting tone
"""

MONGODB_ENHANCEMENT_PROMPT = PromptTemplate(
    input_variables=["question", "raw_response"],
    template=MONGODB_ENHANCEMENT_TEMPLATE
)

# SQL generation prompt with more precise instructions and proper column name/date format
SQL_GENERATION_TEMPLATE = """
Generate MySQL query for NVIDIA stock data.

SCHEMA:
{schema}

SAMPLE DATA:
{sample_data}

QUESTION: {question}

RULES:
1. Return ONLY valid MySQL query
2. Use exact column names with single quotes for names with spaces: Date, 'Adj Close', Close, High, Low, Open, Volume
3. For date values, use format MM/DD/YYYY (e.g., 2000-02-02) in WHERE clauses or do fuzzy match
4. Optimize for query efficiency
5. Add appropriate time period if question implies historical analysis
6. Limit results to 7 rows unless specified otherwise
7. NO explanations, comments or markdown

QUERY:
"""

SQL_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "sample_data", "question"],
    template=SQL_GENERATION_TEMPLATE
)

# SQL enhancement prompt with better structure
SQL_ENHANCEMENT_TEMPLATE = """
Question about NVIDIA stock: {question}

SQL results: {raw_response}

Format your response with:
1. OVERVIEW: One-sentence summary of key finding
2. DATA HIGHLIGHTS: present the figures in point form (prices, dates, % changes) 
3. TREND ANALYSIS: Brief explanation of pattern or trend (if present)
4. CONTEXT: Brief market or company context for these numbers (optional)
5. SQL generated: {raw_response}

Keep response under 150 words, emphasize specific data points, and maintain financial analyst tone.
"""

CHART_ENHANCEMENT_PROMPT = PromptTemplate(
    input_variables=["question", "raw_response"],
    template=SQL_ENHANCEMENT_TEMPLATE
)

CHART_ENHANCEMENT_TEMPLATE = """



"""


CHART_ENHANCEMENT_PROMPT = PromptTemplate(
    input_variables=["question", "raw_response"],
    template=CHART_ENHANCEMENT_TEMPLATE
)


# Improved error handling
ERROR_TEMPLATE = """
Error: {error_message}

Regarding your NVIDIA question: {question}

I couldn't process this request because:
- The specific error relates to {error_message}
- Try rephrasing to focus on either company information or stock performance
- For stock questions, specify time period and metrics of interest
- For company questions, focus on specific business aspects

How else can I help with NVIDIA information?
"""

ERROR_PROMPT = PromptTemplate(
    input_variables=["question", "error_message"],
    template=ERROR_TEMPLATE
)