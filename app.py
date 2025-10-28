import streamlit as st
import os
import pandas as pd
import config as cfg
from conversation_llm import table_metadata, get_relevant_tables, get_generated_sql
from conversation_llm import get_tabular_data

from langchain_openai import ChatOpenAI
import os

os.environ["OPENAI_API_KEY"] = cfg.API_KEY
os.environ["OPENAI_API_BASE"] = cfg.API_BASE
global llm

st.title("💬 Enterprise Data Assistant")
st.caption("🚀 Groq-Powered Streamlit Chatbot for Enterprise Data Exploration")

llm = ChatOpenAI(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0
)

# Create message session
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
if prompt := st.chat_input():
    # Input Prompt from user
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "type":"text", "content": prompt})

    relevant_tables = get_relevant_tables(input_text=prompt, table_names=table_metadata(),llm=llm )
    generated_sql = get_generated_sql(relevant_tables, input_text=prompt, llm=llm)
    tabular_data = get_tabular_data(generated_sql)
    
    sql_prompt = f"""
    You are an assisant that who provides insightful yet easy-to-understand summaries data, Use the following information and summarize the data: 
    DataFrame: {tabular_data}
    Question: {prompt}
    Instructions:
    1. Respond in Humanized tone either use Name ** James ** to address the user or converse like a professional analyst.
    2.The data pertains to Adventure Works Cycles, a company that manufactures and sells bicycles, bicycle parts, and accessories. You assists in analyzing this data as an analyst would.
    3.If the user's question is not related to Adventure Works Cycles, its products, or finances, mention this in your response. However, still summarize the tables provided in this prompt.
    4.If tabular data or dataframe is empty, with no columns or index or If the user's question is not relevant to Adventure Works Cycles, ask clarifying questions to better understand their needs.
    5. Make sure the aggregates of the summary should always be mathematically accurate.
    """ 
       
    response = llm.invoke([{"role": "user", "content": sql_prompt}])
    generated_summary = response.content
    print("--------------------------------------------------------------------")
    print()
    print(generated_summary)
    
    # Output 
    with st.chat_message("assistant"):
        st.write("Here's what I found based on your request:")
        st.write(generated_summary)
    
        sql_header_message = "Here's the SQL query that was generated:\n"
        st.write(sql_header_message)
        st.code(generated_sql, language='sql')
    
        tabular_data_message = "Here’s the data representation based on your request:\n"
        st.write(tabular_data_message)
        st.dataframe(tabular_data)

    st.stop()
