import os
import sqlite3
from operator import itemgetter

import google.generativeai as genai
from sklearn.datasets import fetch_california_housing

from langchain.chains import create_sql_query_chain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.runnables import RunnablePassthrough


class CaliforniaHousingAnalyzer:
    def __init__(self, db_path="mydatabase.db"):
        self.db_path = db_path
        self.db = None
        self.llm = None
        self.write_query_chain = None
        self.validate_chain = None
        self.execute_chain = None
        self.answer_chain = None

    def setup_database(self):
        """Sets up the SQLite database."""
        california_housing_bunch = fetch_california_housing(as_frame=True)
        california_housing_df = california_housing_bunch.frame

        conn = sqlite3.connect(self.db_path)
        california_housing_df.to_sql("housing", conn, index=False)
        self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")

    def define_query_chain(self):
        """Defines the query chain."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest", temperature=0
        )
        self.write_query_chain = create_sql_query_chain(self.llm, self.db)

    def validate_query(self):
        """Validates the query."""
        validate_prompt = PromptTemplate(
            input_variables=["not_formatted_query"],
            template="""You are going to receive a text that contains a SQL query. Extract that query.
            Make sure that it is a valid SQL command that can be passed directly to the Database.
            Avoid using Markdown for this task.
            Text: {not_formatted_query}""",
        )
        self.validate_chain = (
            self.write_query_chain
            | validate_prompt
            | self.llm
            | StrOutputParser()
        )

    def setup_execute_chain(self):
        """Sets up the execute chain."""
        execute_query = QuerySQLDataBaseTool(db=self.db)
        self.execute_chain = self.validate_chain | execute_query

    def setup_answer_chain(self):
        """Sets up the answer chain."""
        answer_prompt = PromptTemplate.from_template(
            """You are going to receive a original user question, generated SQL query, and result of said query. You should use this information to answer the original question. Use only information provided to you.

        Original Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        )

        self.answer_chain = (
            RunnablePassthrough.assign(query=self.validate_chain).assign(
                result=itemgetter("query") | QuerySQLDataBaseTool(db=self.db)
            )
            | answer_prompt
            | self.llm
            | StrOutputParser()
        )

    def run(self, question):
        """Runs the analysis with the given question."""
        return self.answer_chain.invoke({"question": question})


def main():
    # Ensure your API key is set as an environment variable or Colab secret
    os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

    analyzer = CaliforniaHousingAnalyzer()
    analyzer.setup_database()
    analyzer.define_query_chain()
    analyzer.validate_query()
    analyzer.setup_execute_chain()
    analyzer.setup_answer_chain()

    response = analyzer.run("What is the total population?")
    print(response)


if __name__ == "__main__":
    main()