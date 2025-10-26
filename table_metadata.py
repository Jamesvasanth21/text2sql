from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import json


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