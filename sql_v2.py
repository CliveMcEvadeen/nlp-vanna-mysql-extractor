import os
import sqlite3
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough

# Check if GOOGLE_API_KEY is set before assigning
GOOGLE_API_KEY = ''
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

user = "vannauser"
password = "degree477"
host = "localhost"
database = "data"

db = SQLDatabase.from_uri(f"mysql+pymysql://{user}:{password}@{host}/{database}")

def llm():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    return llm

def create_conversation_chain():
    write_query_chain = create_sql_query_chain(llm(), db)
    return write_query_chain

def validate_chain():
    validate_prompt = PromptTemplate(
        input_variables=["not_formatted_query"],
        template="""You are going to receive a text that contains a SQL query. Extract that query.
        Make sure that it is a valid SQL command that can be passed directly to the Database.
        Avoid using Markdown for this task.
        Text: {not_formatted_query}""",
    )
    return create_conversation_chain() | validate_prompt | llm() | StrOutputParser()

def execute_query_and_answer(question):
    execute_query = QuerySQLDataBaseTool(db=db)
    execute_chain = validate_chain() | execute_query

    answer_prompt = PromptTemplate.from_template(
    """You are going to receive an original user question, generated SQL query, and result of said query. You should use this information to answer the original question. Use only information provided to you.

        Original Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )

    answer_chain = (
        RunnablePassthrough.assign(query=validate_chain()).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt | llm() | StrOutputParser()
    )

    print(answer_chain.invoke({"question": question}))

def clean_prompt():
    user_question = input("Please enter your question: ")
    return execute_query_and_answer(user_question)

if __name__ == "__main__":
    while True:
        clean_prompt()
