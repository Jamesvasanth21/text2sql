from pydantic import BaseModel, Field
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate


import os
import json
import pandas as pd
import sqlite3


class Table(BaseModel):
    """Table in SQL database."""
    
    name: str = Field(description="Name of the table in SQL database.")
    description: str = Field(description="Description of the table's purpose or content.")
    columns: list[str] = Field(description="List of columns in the table.")
    
    class Config:
        extra = "ignore"



class RelevantTables(BaseModel):
    """List of all SQL tables relevant to the user's query."""
    tables: list[Table] = Field(
        description="A list of Table objects, where each Table object represents a relevant SQL table."
    )


def table_metadata():
    # Open and read the JSON file
    metadata_table_desc_path = os.path.join('MetaData', 'table_descriptions.json')
    with open(metadata_table_desc_path, 'r') as file:
        data = json.load(file)

    table_dict = data['tables']

    # Open and read the JSON file
    metadata_table_columns_path = os.path.join('MetaData', 'table_columns.json')
    with open(metadata_table_columns_path, 'r') as file:
        data = json.load(file)

    table_column_dict = data['tables']

    tables_columns_list = []
    
    for temp_table_dict in table_dict:
        table_name = temp_table_dict['tableName']
        table_description = temp_table_dict['description']
        table_columns = [column for temp_table_column_dict in table_column_dict if table_name == temp_table_column_dict['tableName'] for column in temp_table_column_dict['columns']]

        
        tables_columns_list.append(Table(name=table_name, description=table_description, columns=table_columns))


    # Assuming db.get_usable_table_names() returns a list of table names
    table_names = "\n".join([f"Table Name: {table.name}, Description: {table.description}, Columns: {table.columns}" for table in tables_columns_list])


    return table_names



def get_relevant_tables(input_text, table_names, llm):
    # This forces the LLM to return a JSON object conforming to the RelevantTables Pydantic schema.
    llm_structured = llm.with_structured_output(RelevantTables)

    system = f"""
    You are an AI designed to assist with SQL database queries. Your task is to return the names of all SQL tables that might be relevant to the user's query. Use the descriptions of the tables mentioned below to understand their purpose and match them with the user's query. The tables, their descriptions and column names are as follows: {table_names}.

    Instructions:
    1. The data pertains to Adventure Works Cycles. If the user question is not regarding the companies products, simply state that there are no relevant tables by returning an empty list in the JSON.
    2. Include all potentially relevant tables.
    3. Match the descriptions with the user's query to ensure accuracy.
    4. Do not hallucinate information.
    5. Use the output format provided by the JSON schema.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{input}"),
        ]
    )
    
    # Define and Execute the chain
    # The chain now is: Prompt -> LLM (forced JSON output)
    table_chain = prompt | llm_structured

    try:
        # Execute the chain
        # The response is now a RelevantTables Pydantic object
        response_object = table_chain.invoke({"input": input_text})
        
        relevant_tables = response_object.tables
        
        print("\n--- LLM Relevant Table Response ---")
        # Print the data received from the LLM, formatted nicely
        print(json.dumps([t.dict() for t in relevant_tables], indent=2))
        
        return relevant_tables
        
    except Exception as e:
        print(f"\nERROR: Failed to invoke structured chain. Ensure GROQ_API_KEY is correct.")
        print(f"Details: {e}")
        return None
    

def get_generated_sql(filtered_table_names, input_text, llm):
    sql_prompt = f"""
        You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run that would return the answer to the input question.

        Instructions:
        1.Unless the user specifies a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per SQLite. The SQL should be runnable without any syntax errors.
        2.Add a total sum at the end for all the calculations.
        3.Order the results to return the most informative data in the database.
        4.Never query for all columns from a table. Query only the columns needed to answer the question.
        5.Use only the column names visible in the tables below.
        6.Be careful not to query for columns that do not exist. Pay attention to which column is in which table.
        7.Use the date('now') function to get the current date if the question involves "today".
        8.The data pertains to Adventure Works Cycles, a company that manufactures and sells bicycles, bicycle parts, and accessories. 9.You are an AI assistant that helps in analyzing this data as an analyst would.
        10.If the user's question is not related to Adventure Works Cycles, its products, or finances, mention this in your response and ask clarifying questions to better understand their needs.
        11.I don't need the step-by-step thought process and the output should always be of the below mentioned format.
        Format:

        Question: [Question here]
        SQLQuery: [SQL Query to run]

        Only use the following tables, table descriptions, and relevant columns:
        {filtered_table_names}

        Question: {input_text}
        """
        
    response = llm.invoke([{"role": "user", "content": sql_prompt}])

    generated_query = response.content

    print(generated_query)

    generated_query = generated_query.split('SQLQuery:')[1]
    generated_query = generated_query.replace('```', '')
    generated_query = generated_query.replace('sql', '')
    
    print("\n--- LLM Generated SQL Response ---")
    print(generated_query)
    
    return generated_query



def get_tabular_data(generated_query):

    try:
        conn = sqlite3.connect('adventureworks.db')
        cursor = conn.cursor()

        cursor.execute(generated_query)
        results = cursor.fetchall()

        # Get column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        conn.close()

        # Create a DataFrame
        df = pd.DataFrame(results, columns=columns)

        # Display the DataFrame
        print(df)
        
        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()