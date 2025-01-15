import os
from operator import itemgetter
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough


class SQLQueryHandler:
    def __init__(self, user, password, host, database, google_api_key):
        # Set environment variables
        os.environ["GOOGLE_API_KEY"] = google_api_key

        # Database connection
        self.db = SQLDatabase.from_uri(f"mysql+pymysql://{user}:{password}@{host}/{database}")

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

    def create_conversation_chain(self):
        """Creates the base conversation chain with the LLM and database."""
        return create_sql_query_chain(self.llm, self.db)

    def validate_chain(self):
        """Builds the chain for validating SQL queries."""
        validate_prompt = PromptTemplate(
            input_variables=["not_formatted_query"],
            template="""You are going to receive a text that contains a SQL query. Extract that query.
            Make sure that it is a valid SQL command that can be passed directly to the Database.
            Avoid using Markdown for this task.
            Text: {not_formatted_query}"""
        )
        return self.create_conversation_chain() | validate_prompt | self.llm | StrOutputParser()

    def execute_query_and_answer(self, question):
        """
        Executes the query generated from the user's question
        and returns the response in natural language.
        """
        # Query execution tool
        execute_query = QuerySQLDataBaseTool(db=self.db)

        # Chain for query execution
        execute_chain = self.validate_chain() | execute_query

        # Prompt for generating the final answer
        answer_prompt = PromptTemplate.from_template(
            """You are going to receive an original user question, generated SQL query, and result of said query. 
            Use this information to answer the original question. Use only information provided to you.

            Original Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )

        # Answer generation chain
        answer_chain = (
            RunnablePassthrough.assign(query=self.validate_chain()).assign(
                result=itemgetter("query") | execute_query
            )
            | answer_prompt | self.llm | StrOutputParser()
        )

        # Execute the chain and print the response
        response = answer_chain.invoke({"question": question})
        print(response)

    def start_interaction(self):
        """Handles user interaction in a loop."""
        print("Welcome to the SQL Query Handler! Type 'exit' to quit.")
        while True:
            user_question = input("Please enter your question: ")
            if user_question.lower() == "exit":
                print("Exiting the SQL Query Handler. Goodbye!")
                break
            self.execute_query_and_answer(user_question)


if __name__ == "__main__":
    # Configuration
    USER = "vannauser"
    PASSWORD = "degree477"
    HOST = "localhost"
    DATABASE = "data"
    GOOGLE_API_KEY = "AIzaSyDN5BCWKiyOUdx3_xRa5b9szL8muDcfSlU"

    # Initialize and start the handler
    sql_handler = SQLQueryHandler(USER, PASSWORD, HOST, DATABASE, GOOGLE_API_KEY)
    sql_handler.start_interaction()
