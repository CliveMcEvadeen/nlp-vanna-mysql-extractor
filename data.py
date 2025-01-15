from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
from vanna import *
from dotenv import load_dotenv
import os

load_dotenv()

class MyLadda(ChromaDB_VectorStore, GoogleGeminiChat):
    """
    A class combining ChromaDB_VectorStore and GoogleGeminiChat functionality.
    This class integrates database connection, schema exploration, training data management, and LLM communication.
    """
    def __init__(self, chromadb_config=None, gemini_config=None):
        ChromaDB_VectorStore.__init__(self, config=chromadb_config)
        GoogleGeminiChat.__init__(self, config=gemini_config)

    def connect_to_database(self, host, dbname, user, password, port):
        """
        Connects to a MySQL database.
        """
        self.connect_to_mysql(host=host, dbname=dbname, user=user, password=password, port=port)
        print(f"Connected to database '{dbname}' at host '{host}'.")

    def fetch_information_schema(self):
        """
        Fetches the database information schema and returns it as a DataFrame.
        """
        query = "SELECT * FROM INFORMATION_SCHEMA.COLUMNS"
        df = self.run_sql(query)
        print("Fetched information schema.")
        return df

    def create_training_plan(self, schema_df):
        """
        Generates a training plan based on the information schema DataFrame.
        """
        plan = self.get_training_plan_generic(schema_df)
        print("Training plan generated.")
        return plan

    def train_ddl(self, ddl):
        """
        Adds DDL statements to the training data.
        """
        self.train(ddl=ddl)
        print("DDL training data added.")

    def train_documentation(self, documentation):
        """
        Adds business-specific documentation to the training data.
        """
        self.train(documentation=documentation)
        print("Documentation training data added.")

    def train_sql(self, sql):
        """
        Adds SQL queries to the training data.
        """
        self.train(sql=sql)
        print("SQL training data added.")

    def get_all_training_data(self):
        """
        Retrieves all training data currently available in the system.
        """
        training_data = self.get_training_data()
        print("Fetched all training data.")
        return training_data

    def remove_training_data_by_id(self, data_id):
        """
        Removes training data by its unique identifier.
        """
        self.remove_training_data(id=data_id)
        print(f"Removed training data with ID: {data_id}.")

    def env(variable_name, modale_name):
        return os.getenv(variable_name=None, modale_name=None)

# Usage
if __name__ == "__main__":

    import os
    from dotenv import load_dotenv
    load_dotenv()

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL =  os.getenv('GEMINI_MODEL')
    # Initialize MyVanna
    vn = MyLadda(
        chromadb_config=None,
        gemini_config={'api_key': GEMINI_API_KEY, 'model': GEMINI_MODEL}
    )

    # configuration


    # Connect to MySQL database
    vn.connect_to_database(
        host='localhost',
        dbname='data',
        user='vannauser',
        password='degree477',
        port=3306
    )

    # Fetch and inspect the information schema
    schema_df = vn.fetch_information_schema()
    print(schema_df)

    # # Create a training plan
    # training_plan = vn.create_training_plan(schema_df)
    # print(training_plan)

    # Optional: Train the system using the generated plan
    # vn.train(plan=training_plan)

    # Add specific training data
    # vn.train_ddl("""
    #     CREATE TABLE IF NOT EXISTS my_table (
    #         id INT PRIMARY KEY,
    #         name VARCHAR(100),
    #         age INT
    #     )
    # """)

    # vn.train_documentation(
    #     "Our business defines OTIF score as the percentage of orders that are delivered on time and in full."
    # )

    # vn.train_sql("SELECT * FROM my_table WHERE name = 'John Doe'")

    # # Inspect current training data
    # training_data = vn.get_all_training_data()
    # print(training_data)

    # # Remove obsolete training data
    # vn.remove_training_data_by_id('1-ddl')
    # sql = vn.generate_sql(question='what is there?')
    # print(sql)
    vn.ask(question='is there any data in the database')

    # from vanna.flask import VannaFlaskApp
    # app = VannaFlaskApp(vn)
    # app.run()
