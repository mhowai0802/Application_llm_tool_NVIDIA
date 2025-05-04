# sql_tool.py
from sqlalchemy import create_engine, MetaData, text
import config
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
import pymysql
pymysql.install_as_MySQLdb()

def generate_sql(query: str) -> str:
    """Generates and executes SQL queries for NVIDIA stock information using LLM."""
    try:
        engine = create_engine(config.CONFIG["sql_database"]["connection_string"])
        metadata = MetaData()
        table_name = config.CONFIG["sql_database"]["table_name"]
        # Test connection and get schema information
        try:
            with engine.connect() as conn:
                # Extract database name from connection string
                db_name = config.CONFIG["sql_database"]["connection_string"].split('/')[-1]
                if '?' in db_name:  # Handle query parameters in connection string
                    db_name = db_name.split('?')[0]
                check_table_query = text(f"""
                     SELECT TABLE_NAME 
                     FROM information_schema.TABLES 
                     WHERE TABLE_SCHEMA = '{db_name}'
                 """)
                # Check if table exists
                result = conn.execute(check_table_query, {
                    "db_name": db_name,
                    "table_name": table_name
                }).fetchone()
                if not result:
                    return f"The table '{table_name}' doesn't appear to exist in the MySQL database."
                # Get sample data for context
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = conn.execute(sample_query).fetchall()
                sample_headers = conn.execute(sample_query).keys()
                # Format sample data
                sample_data = "| " + " | ".join(str(h) for h in sample_headers) + " |\n"
                sample_data += "| " + " | ".join("---" for _ in sample_headers) + " |\n"
                for row in sample_rows:
                    sample_data += "| " + " | ".join(str(value) for value in row) + " |\n"

        except Exception as conn_err:
            return f"Error connecting to database: {str(conn_err)}"

        # Define schema information based on the provided schema
        schema_info = f"""
        Table: {table_name}
        Columns:
        - Date (date): The trading date
        - Adj Close (float): Adjusted closing price
        - Close (float): Closing price
        - High (float): Highest price during the day
        - Low (float): Lowest price during the day
        - Open (float): Opening price
        - Volume (int): Trading volume for the day
        """

        # Import the SQL generation prompt from prompt.py
        from utils.prompt import SQL_GENERATION_PROMPT

        # Initialize the LLM for SQL generation
        llm = Ollama(
            model=config.CONFIG["ollama"]["model"],
            base_url=config.CONFIG["ollama"]["base_url"],
            temperature=0.1  # Lower temperature for more deterministic SQL generation
        )

        # Create LLM chain with the imported prompt
        sql_generation_chain = LLMChain(
            llm=llm,
            prompt=SQL_GENERATION_PROMPT
        )
        # Generate SQL with LLM chain
        generated_sql = sql_generation_chain.run(
            schema=schema_info,
            sample_data=sample_data,
            question=query
        ).strip()
        # Clean up the generated SQL if needed
        if generated_sql.startswith("```sql"):
            generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

        # Execute the generated query
        query_result = "No results"
        with engine.connect() as conn:
            try:
                result = conn.execute(text(generated_sql))
                rows = result.fetchall()

                if not rows:
                    query_result = "Query executed successfully but returned no results."
                else:
                    # Format the result as a table
                    headers = result.keys()

                    # Create header row
                    query_result = "| " + " | ".join(str(h) for h in headers) + " |\n"

                    # Create separator row
                    query_result += "| " + " | ".join("---" for _ in headers) + " |\n"

                    # Create data rows
                    for row in rows:
                        query_result += "| " + " | ".join(str(value) for value in row) + " |\n"

            except Exception as exec_error:
                query_result = f"Error executing query: {str(exec_error)}\n\nGenerated SQL may have syntax errors or incompatible functions."

                # For debugging, provide a simplified query as fallback
                try:
                    fallback_sql = f"SELECT * FROM {table_name} ORDER BY Date DESC LIMIT 5"
                    result = conn.execute(text(fallback_sql))
                    rows = result.fetchall()

                    if rows:
                        query_result += "\n\nFallback query executed successfully. Here's recent data:\n\n"
                        headers = result.keys()
                        query_result += "| " + " | ".join(str(h) for h in headers) + " |\n"
                        query_result += "| " + " | ".join("---" for _ in headers) + " |\n"
                        for row in rows:
                            query_result += "| " + " | ".join(str(value) for value in row) + " |\n"
                except:
                    pass  # If fallback also fails, just use the original error

        # Prepare the complete response with the actual query and results
        full_response = f"""
        ## SQL Query Results for NVIDIA Stock Data
        
        ### Query Details
        The following SQL query was generated by AI to answer your question:
        
        ```sql
        {generated_sql}
        Results
        {query_result}
        
        This query was dynamically generated based on your question: "{query}"
        """


        return full_response

    except Exception as e:
        return f"""
        Error Querying NVIDIA Stock Data
        Error: {str(e)}
        
        This could be because:
        
        The database connection string is incorrect
        The required database driver (pymysql) is not installed
        The table structure doesn't match what was expected (Date, Adj Close, Close, High, Low, Open, Volume)
        There might be an issue with generating valid SQL for your question
        Please check your configuration or try rephrasing your question.
        """