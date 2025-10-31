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

The application provides web interfaces to view all entities and relationships in the ESGTrader database:

- **`/`** - Home page with navigation links to all tables
- **`/stocks`** - View all stocks (stock_id, ticker, sector)
- **`/investors`** - View all investors (investor_id, company_name)
- **`/transactions`** - View all transactions (investor_id, stock_id, transaction_time, transaction_type, unit_price, unit_number)
- **`/holdings`** - View all holdings (stock_id, portfolio_id, average_price, holding_count)
- **`/portfolios`** - View all portfolios (portfolio_id, investor_id, total_value, creation_date)
- **`/risk_metrics`** - View all risk metrics (portfolio_id, metric_date, sharpe_ratio, beta, volatility, var)
- **`/macro_data`** - View all macro data (macro_date, risk_free_rate, interest_rate)
- **`/stock_prices`** - View all stock prices (stock_id, price_date, daily_price)
- **`/esg_scores`** - View all ESG scores (stock_id, score_date, esg_score)

## Database Schema

The application interacts with the following tables:
- **stock** - Stock information
- **investor** - Investor/company information
- **transaction** - Buy/sell transactions
- **portfolio** - Investment portfolios
- **holdings** - Stocks held in portfolios
- **risk_metrics** - Portfolio risk metrics over time
- **daily_macro_data** - Macroeconomic indicators
- **stock_price** - Historical stock prices
- **esg_score** - ESG (Environmental, Social, Governance) scores

## Project Structure

```
db4111/
├── server.py                  # Main Flask application
├── templates/                 # Jinja2 templates
│   ├── index.html            # Homepage
│   ├── stocks.html           # Stocks table view
│   ├── investors.html        # Investors table view
│   ├── transactions.html     # Transactions table view
│   ├── holdings.html         # Holdings table view
│   ├── portfolios.html       # Portfolios table view
│   ├── risk_metrics.html     # Risk metrics table view
│   ├── macro_data.html       # Macro data table view
│   ├── stock_prices.html     # Stock prices table view
│   └── esg_scores.html       # ESG scores table view
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore file (includes venv/)
└── README.md                 # This file
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

## Troubleshooting

### Virtual Environment Issues
If you see both `(venv)` and `(base)` in your terminal prompt:
```bash
# Deactivate conda first
conda deactivate

# Then activate only the venv
source venv/bin/activate
```

### Database Connection Errors
- Make sure you've updated the `DATABASE_USERNAME` and `DATABASE_PASSWRD` in `server.py` (lines 33-34)
- Verify your credentials can connect to the PostgreSQL server
- Check that the database tables exist and contain data

### Module Not Found Errors
If you get `ModuleNotFoundError`, make sure you're in the virtual environment and have installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```
