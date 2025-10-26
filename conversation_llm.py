from pydantic import BaseModel, Field
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate


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


def table_metadata():
    # Open and read the JSON file
    with open('MetaData/table_description.json', 'r') as file:
        data = json.load(file)

    table_dict = data['tables']

    # Open and read the JSON file
    with open('MetaData/table_columns.json', 'r') as file:
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
    
    system = f"""
    You are an AI designed to assist with SQL database queries. Your task is to return the names of all SQL tables that might be relevant to the user's query. Use the descriptions  of the tables mentioned below to understand their purpose and match them with the user's query. The tables, their descriptions and column names are as follows: {table_names}.

    Instructions:
    1.The data pertains to Adventure Works Cycles, a company that manufactures and sells bicycles, bicycle parts, and accessories. The AI assists in analyzing this data as an analyst would. If the user question is not regarding the companies products, , simply state that there are no relevant tables. 
    2.Include all potentially relevant tables and columns, even if you're not entirely sure they are needed.
    3.Use the table descriptions to determine relevance to the user's query.
    4.Match the descriptions with the user's query to ensure accuracy.
    5.Do not hallucinate information. If there are no relevant tables or columns for the user's query, simply state that there are no relevant tables.   
    6.Use only table names and column names that are available in description, do not hallucinate on the table names and column names
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{input}"),
        ]
    )
    
    print(system)
    
    
    # Bind tools to the language model
    llm_with_tools = llm.bind_tools([Table])

    # Set up the output parser
    output_parser = PydanticToolsParser(tools=[Table])

    # Define the chain
    table_chain = prompt | llm_with_tools | output_parser

    # Execute the chain
    response = table_chain.invoke({"input": input_text})
    
    print(response)
    
    return response
    

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
        Format:

        Question: [Question here]
        SQLQuery: [SQL Query to run]

        Only use the following tables, table descriptions, and relevant columns:
        {filtered_table_names}

        Question: {input_text}
        """
        
    response = llm([{"role": "user", "content": sql_prompt}])

    generated_query = response.content

    generated_query = generated_query.split(':')[1]
    generated_query = generated_query.replace('```', '')
    generated_query = generated_query.replace('sql', '')
    
    print("")
    print(f"Question: {input_text}")
    print(generated_query)
    print("")
    
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