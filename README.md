# ESGTrader - Database Project Part 3

Flask web application for ESGTrader using PostgreSQL.

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

Create and activate a Python virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 2. Install Dependencies

First, make sure you have Python 3 installed:
```bash
python3 --version
```

Install the required packages:
```bash
pip install -r requirements.txt
```

**Note**: Once the virtual environment is activated, you can use `pip` instead of `pip3`.

### 3. Configure Database Connection

Edit `server.py` and update the `DATABASEURI` variable with your PostgreSQL credentials:

```python
DATABASEURI = "postgresql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST/YOUR_DATABASE"
```

For example:
```python
DATABASEURI = "postgresql://myuser:mypass@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"
```

### 4. Run the Application

Start the Flask server:
```bash
python server.py
```

By default, the server runs on `http://0.0.0.0:8111`. Open your browser and navigate to:
```
http://localhost:8111
```

### 5. Development

To run in debug mode:
```bash
python server.py --debug
```

To deactivate the virtual environment when done:
```bash
deactivate
```

## Available Pages

- **`/`** - Home page with navigation links
- **`/stocks`** - View all stocks (ready for database integration)

## Project Structure

```
db4111/
├── server.py              # Main Flask application
├── templates/             # Jinja2 templates
│   ├── index.html        # Homepage
│   └── stocks.html       # All stocks page
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file (includes venv/)
└── README.md             # This file
```

## Dependencies

- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.23** - Database connection (no ORM features used)
- **psycopg2-binary 2.9.9** - PostgreSQL database adapter for Python
- **click 8.1.7** - Command-line interface

## Notes

- This application uses SQLAlchemy for database connection but **does not use ORM features**
- All database queries must be written as raw SQL strings
- The connection is established before each request and closed after each request
- `psycopg2-binary` is the PostgreSQL driver that SQLAlchemy uses to communicate with the database