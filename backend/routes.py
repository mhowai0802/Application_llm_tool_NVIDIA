# backend/routes.py
from flask import Blueprint, request, jsonify
import requests
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
import config
from tools.mongodb_tool import retrieve_from_mongodb
from tools.sql_tool import generate_sql
from tools.chart_tool import retrieve_chart
import utils.prompt as prompt


api_bp = Blueprint('api', __name__)

# API connection details
apiKey = config.CONFIG["api"]["key"]  # Get from config
basicUrl = "https://genai.hkbu.edu.hk/general/rest"
modelName = "gpt-4-o-mini"
apiVersion = "2024-05-01-preview"


# Function to call the LLM API
def call_llm_api(message):
    conversation = [{"role": "user", "content": message}]
    url = basicUrl + "/deployments/" + modelName + "/chat/completions/?api-version=" + apiVersion
    headers = {'Content-Type': 'application/json', 'api-key': apiKey}
    payload = {'messages': conversation}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Extract the response text - adjust depending on the exact API response structure
        return data['choices'][0]['message']['content']
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


# Create a router function to decide which tool to use
def route_query(question):
    router_prompt = prompt.ROUTER_PROMPT.format(question=question)
    tool_choice = call_llm_api(router_prompt).strip().lower()
    return tool_choice


# Function to process the query through the appropriate tool
def process_query(question):
    try:
        # First determine the tool to use
        tool_choice = route_query(question)

        # Use the selected tool
        if 'mongodb' in tool_choice:
            tool_name = "MongoDB Retriever"
            raw_response = retrieve_from_mongodb(question)
            enhancement_prompt = prompt.MONGODB_ENHANCEMENT_PROMPT.format(
                question=question,
                raw_response=raw_response
            )
        elif 'sql' in tool_choice:
            tool_name = "SQL Generator"
            raw_response = generate_sql(question)
            enhancement_prompt = prompt.SQL_ENHANCEMENT_PROMPT.format(
                question=question,
                raw_response=raw_response
            )
        elif 'chart' in tool_choice:
            tool_name = "Chart Retreiver"
            raw_response = retrieve_chart(question)
            # enhancement_prompt = prompt.CHART_ENHANCEMENT_TEMPLATE.format(
            #     question=question,
            #     raw_response=raw_response
            # )
            return raw_response, tool_name
        else:
            # Fallback to a general response
            tool_name = "General Response"
            general_prompt = prompt.GENERAL_PROMPT.format(question=question)
            return call_llm_api(general_prompt), tool_name

        # Enhance the response with the appropriate prompt
        enhanced_response = call_llm_api(enhancement_prompt)
        enhanced_response = enhanced_response.replace("## SQL Query Results for NVIDIA Stock Data","")
        return enhanced_response, tool_name

    except Exception as e:
        # Handle errors gracefully
        tool_name = "Error Handler"
        error_prompt = prompt.ERROR_PROMPT.format(question=question, error_message=str(e))
        return call_llm_api(error_prompt), tool_name


@api_bp.route('/api/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    question = data['query']
    response, tool_used = process_query(question)
    return jsonify({
        "response": response,
        "tool_used": tool_used
    })