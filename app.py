import streamlit as st
import os
import pandas as pd
import config as cfg

from langchain_openai import ChatOpenAI
import os

os.environ["OPENAI_API_KEY"] = cfg.API_KEY
os.environ["OPENAI_API_BASE"] = cfg.API_BASE

llm = ChatOpenAI(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0
)



from conversation_llm import table_metadata, get_relevant_tables, get_generated_sql
from conversation_llm import get_tabular_data

from langchain.memory import ConversationBufferMemory
from difflib import SequenceMatcher

st.title("💬 Enterprise Data Assistant")
st.caption("🚀 Groq-Powered Streamlit Chatbot for Enterprise Data Exploration")


# Create memory session
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
   
    
# Create message session
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# Function to add a new chat session
def add_chat_session():
    llm = ChatOpenAI(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0
    )
    
    st.session_state.memory = ConversationBufferMemory()
    st.session_state["messages"] = []


st.sidebar.title("Enterprise Data Assistant")

# Add a button to the sidebar
if st.sidebar.button("➕"):
    add_chat_session()
    

if st.session_state.messages:
    print(st.session_state.messages)
    for msg in st.session_state.messages:       
        if msg["role"] == "user":
            st.chat_message("user").write(msg['content'])
        elif msg["role"] == "assistant":
            if msg['type'] == "text":
                st.chat_message("user").write(msg['content'])
            elif msg['type'] == "response":
                with st.chat_message("assistant"):
                    st.write("Here is the summary for the prompt:\n")
                    st.write(msg['summary'])
                
                    sql_header_message = "Here is the generated SQL query:\n"
                    st.write(sql_header_message)
                    st.code(msg['sql'], language='sql')
                
                    tabular_data_message = "Here is the tablular data for the prompt:"
                    st.write(tabular_data_message)
                    st.dataframe(msg['dataframe'])
                    
                    

llm = ChatOpenAI(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0
)
    

# Function to check if the new query is similar to any previous ones 
def check_similarity(new_query, threshold=0.85):
    history = st.session_state.memory.buffer
    records = history.split("\n")
    
    past_inputs = [record.split(":")[1].strip() for record in records if "Human" in record]
    
    past_outputs = [record.split(":")[1].strip() for record in records if "AI" in record]
    
    for past_input, past_output in zip(past_inputs, past_outputs):
        similarity = SequenceMatcher(None, new_query, past_input).ratio()
        print("Similarity Score for current user input")
        if similarity > threshold:
           for msg in st.session_state.messages:       
                if msg["role"] == "assistant":
                    print(msg)
                    if msg['type'] == "response":
                        print(msg)
                        if past_output == msg["summary"]:
                            sql = msg["sql"]
                            dataframe = msg["dataframe"]
                            summary = msg["summary"]
                            
                            return {"sql":sql, "dataframe": dataframe, "summary": summary}, similarity
        
    return None, 0
  
    
    
if prompt := st.chat_input():
    # Step 1: Check for similarity 
    prev_response, similarity_score = check_similarity(prompt)
    
    # Step 2: Display response 
    # Input Prompt from user
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "type":"text", "content": prompt})

    if prev_response:
        # If similar response found, display it
        generated_sql = prev_response["sql"]
        tabular_data = prev_response["dataframe"]
        generated_summary = prev_response["summary"]
        
        # Output 
        with st.chat_message("assistant"):
            st.write("Here is the summary for the prompt:\n")
            st.write(generated_summary)
        
            sql_header_message = "Here is the generated SQL query:\n"
            st.write(sql_header_message)
            st.code(generated_sql, language='sql')
        
            tabular_data_message = "Here is the tablular data for the prompt:"
            st.write(tabular_data_message)
            st.dataframe(tabular_data)
            
    else:
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
        response = llm([{"role": "user", "content": sql_prompt}])
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
      
    
    
    st.session_state.messages.append({
        "role": "assistant", 
        "type": "response",
        "summary": generated_summary,
        "sql": generated_sql, 
        "dataframe": tabular_data.to_dict('records')
    })
    
    response_dict = {
        "role": "assistant", 
        "type": "response",
        "summary": generated_summary,
        "sql": generated_sql, 
        "dataframe": tabular_data.to_dict('records')
    }
    
    st.session_state.memory.save_context(
        {"input": prompt},
        {"output": generated_summary}
    )
    
    
    llm.bind(memory=st.session_state.memory)
    st.stop()
