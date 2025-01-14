# LADDA Database Assistant

## Description
LADDA Database Assistant is a project that integrates ChromaDB for vector storage and Google Gemini for AI communication. It allows users to connect to MySQL databases, explore schemas, and manage training data for AI models.

## Features
- Connect to MySQL databases
- Fetch and analyze database schemas
- Generate training plans based on schema data
- Manage various types of training data (DDL, documentation, SQL)
- Interact with the database using natural language queries

## Installation
To set up the project, clone the repository and install the required dependencies. Check the `requirements.txt` file for the necessary packages.

```bash
pip install -r requirements.txt
```

## Usage
To use the LADDA Database Assistant, initialize the `MyLadda` class and connect to your MySQL database:

```python
from data import MyLadda

# Initialize MyLadda
vn = MyLadda(chromadb_config=None, gemini_config={'api_key': 'YOUR_API_KEY', 'model': 'gemini-1.5-flash'})

# Connect to MySQL database
vn.connect_to_database(host='localhost', dbname='your_db', user='your_user', password='your_password', port=3306)
```

## Dependencies
Please refer to the `requirements.txt` file for the list of required packages.

## Environment Variables
Ensure to configure any necessary environment variables in the `.env` file.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.
