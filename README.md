# Flask-Laravel SQL Query Processor

This project facilitates seamless interaction between a Laravel application and a MySQL database through a Flask-based Python API. It leverages the LangChain framework and Google Gemini LLM for natural language processing, enabling users to send queries in plain English and receive meaningful database responses. The project also incorporates session management to optimize performance and reduce memory overhead.

---

## Features

1. **Natural Language Query Processing**:
   - Accepts plain English queries.
   - Converts queries into SQL using Google Gemini LLM.

2. **Database Integration**:
   - Interacts with a MySQL database hosted on XAMPP.

3. **Session Management**:
   - Stores query history and interactions in sessions to optimize performance.

4. **Seamless Laravel Integration**:
   - Provides an API endpoint for Laravel applications to communicate with the system.

5. **Interaction History**:
   - Retrieves past interactions for user review.

---

## Technologies Used

### Backend
- **Python**:
  - Flask: RESTful API framework.
  - SQLite/MySQL: Database management and interaction.
  - LangChain: Chain-based processing of natural language queries.
  - Google Gemini LLM: For language understanding and query generation.

### Frontend
- **Laravel**:
  - HTTP client for API interaction.
  - Blade templates for UI representation.

---

## Installation

### Prerequisites
1. Python 3.8+
2. Flask
3. XAMPP (MySQL server)
4. Laravel 8+
5. Google Gemini API Key (obtain from Google Generative AI).

---

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/flask-laravel-sql-processor.git
cd flask-laravel-sql-processor
```

#### 2. Install Python Dependencies
```bash
pip install flask flask-session langchain langchain-google-genai pymysql
```

#### 3. Configure MySQL Database
- Start XAMPP and ensure MySQL is running.
- Create a database (`data`) in MySQL.
- Update database credentials in `SQLQueryHandler` in `app.py`.

```python
user = "your_mysql_username"
password = "your_mysql_password"
host = "localhost"
database = "data"
```

#### 4. Set Google API Key
- Replace `GOOGLE_API_KEY` in `app.py` with your API key.

```python
GOOGLE_API_KEY = 'your-google-api-key'
```

#### 5. Run the Flask Application
```bash
python app.py
```
- The server will start at `http://127.0.0.1:5000`.

---

### Laravel Integration

#### 1. Install Laravel HTTP Client
Ensure your Laravel project has the HTTP client installed:
```bash
composer require guzzlehttp/guzzle
```

#### 2. Create a Service for API Interaction
Create a service to interact with the Flask API.

```php
use Illuminate\Support\Facades\Http;

class SQLProcessorService
{
    public static function queryDatabase($question)
    {
        $response = Http::post('http://127.0.0.1:5000/query', [
            'question' => $question,
        ]);

        return $response->json();
    }

    public static function getHistory()
    {
        $response = Http::get('http://127.0.0.1:5000/history');
        return $response->json();
    }
}
```

#### 3. Use the Service in a Controller
```php
use App\Services\SQLProcessorService;

public function queryDatabase(Request $request)
{
    $question = $request->input('question');
    $response = SQLProcessorService::queryDatabase($question);

    return view('results', ['response' => $response]);
}

public function getHistory()
{
    $history = SQLProcessorService::getHistory();

    return view('history', ['history' => $history['history']]);
}
```

#### 4. Create Blade Templates
- `results.blade.php`: Display query results.
- `history.blade.php`: Display interaction history.

---

## API Endpoints

### 1. `/query` (POST)
- **Description**: Processes user queries.
- **Input**:
  ```json
  {
    "question": "What is the total population?"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "response": "The total population is 500,000."
  }
  ```

### 2. `/history` (GET)
- **Description**: Retrieves query history.
- **Response**:
  ```json
  {
    "history": [
      {"question": "What is the total population?", "response": "500,000"}
    ]
  }
  ```

---

## Security Considerations

1. **Environment Variables**:
   - Use `.env` files for storing sensitive data such as database credentials and API keys.
   - For Flask, use `python-dotenv`.

2. **SQL Injection Prevention**:
   - Input validation and sanitization are handled by LangChain.

3. **Rate Limiting**:
   - Implement Flask middleware to limit API requests.

---

## Future Enhancements

1. **Authentication**:
   - Add API key-based authentication for secure Laravel-Flask communication.

2. **Error Handling**:
   - Enhance error handling for edge cases and invalid inputs.

3. **Scalability**:
   - Use a production-grade WSGI server like Gunicorn for deploying Flask.

4. **Caching**:
   - Implement Redis for caching results of frequently asked queries.

5. **Front-End Integration**:
   - Provide a React or Vue.js front-end for Laravel integration.

---

## License

This project is licensed under the MIT License.

---

## Contact

For issues and contributions, contact [clivekakeeto47@gmail.com].