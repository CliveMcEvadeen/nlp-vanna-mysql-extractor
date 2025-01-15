from flask import Flask, request, jsonify, session
from flask_session import Session
import os
from operator import itemgetter
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough

app = Flask(__name__)

# Session Configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "your_secret_key"
Session(app)


class SQLQueryHandler:
    def __init__(self, user, password, host, database, google_api_key):
        os.environ["GOOGLE_API_KEY"] = google_api_key
        self.db = SQLDatabase.from_uri(f"mysql+pymysql://{user}:{password}@{host}/{database}")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

    def create_conversation_chain(self):
        return create_sql_query_chain(self.llm, self.db)

    def validate_chain(self):
        validate_prompt = PromptTemplate(
            input_variables=["not_formatted_query"],
            template="""You are going to receive a text that contains a SQL query. Extract that query.
            Make sure that it is a valid SQL command that can be passed directly to the Database.
            Avoid using Markdown for this task.
            Text: {not_formatted_query}"""
        )
        return self.create_conversation_chain() | validate_prompt | self.llm | StrOutputParser()

    def execute_query_and_answer(self, question):
        execute_query = QuerySQLDataBaseTool(db=self.db)
        execute_chain = self.validate_chain() | execute_query

        answer_prompt = PromptTemplate.from_template(
            """You are going to receive an original user question, generated SQL query, and result of said query. 
            Use this information to answer the original question. Use only information provided to you.

            Original Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )

        answer_chain = (
            RunnablePassthrough.assign(query=self.validate_chain()).assign(
                result=itemgetter("query") | execute_query
            )
            | answer_prompt | self.llm | StrOutputParser()
        )

        response = answer_chain.invoke({"question": question})
        return response


# Initialize SQLQueryHandler
sql_handler = SQLQueryHandler(
    user="vannauser",
    password="degree477",
    host="localhost",
    database="data",
    google_api_key="AIzaSyDN5BCWKiyOUdx3_xRa5b9szL8muDcfSlU"
)


@app.route("/query", methods=["POST"])
def handle_query():
    # Retrieve user question from the POST request
    user_question = request.json.get("question")

    # Check if sessions contain previous interactions
    if "history" not in session:
        session["history"] = []

    try:
        # Process the user question
        response = sql_handler.execute_query_and_answer(user_question)

        # Store interaction in session
        session["history"].append({"question": user_question, "response": response})

        return jsonify({"status": "success", "response": response})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    """Retrieve the interaction history from the session."""
    return jsonify({"history": session.get("history", [])})


if __name__ == "__main__":
    app.run(debug=True)
