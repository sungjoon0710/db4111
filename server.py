
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
from datetime import datetime, date
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.139.8.30/proj1part2
#
# For example, if you had username ab1234 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://ab1234:123123@34.139.8.30/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "jl6316"
DATABASE_PASSWRD = "021024"
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	#
	# example of a database query
	#
	select_query = "SELECT name from test"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result[0])
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
	return render_template("another.html")


@app.route('/new_investor')
def new_investor():
	"""
	Page for creating new investor portfolios
	"""
	# Get confirmation message if redirected from add
	confirmation = request.args.get('confirmation', '')
	investor_id = request.args.get('investor_id', '')
	company_name = request.args.get('company_name', '')
	portfolio_id = request.args.get('portfolio_id', '')
	
	context = dict(
		confirmation=confirmation,
		investor_id=investor_id,
		company_name=company_name,
		portfolio_id=portfolio_id
	)
	return render_template("new_investor.html", **context)


@app.route('/manage_investor')
def manage_investor():
	"""
	Page for managing existing investor records - update or delete
	"""
	# Get all investors for the dropdown
	select_query = "SELECT investor_id, company_name FROM investor ORDER BY investor_id"
	cursor = g.conn.execute(text(select_query))
	investors_list = []
	for result in cursor:
		investors_list.append({'investor_id': result[0], 'company_name': result[1]})
	cursor.close()
	
	# Get selected investor details if an investor_id is provided
	selected_investor_id = request.args.get('investor_id', '')
	selected_investor = None
	portfolio_count = 0
	
	if selected_investor_id:
		# Get investor details
		investor_query = "SELECT investor_id, company_name FROM investor WHERE investor_id = :investor_id"
		cursor = g.conn.execute(text(investor_query), {"investor_id": selected_investor_id})
		result = cursor.fetchone()
		if result:
			selected_investor = {'investor_id': result[0], 'company_name': result[1]}
		cursor.close()
		
		# Count portfolios for this investor
		portfolio_query = "SELECT COUNT(*) FROM portfolio WHERE investor_id = :investor_id"
		cursor = g.conn.execute(text(portfolio_query), {"investor_id": selected_investor_id})
		portfolio_count = cursor.fetchone()[0]
		cursor.close()
	
	# Get confirmation messages
	confirmation = request.args.get('confirmation', '')
	message = request.args.get('message', '')
	
	context = dict(
		investors=investors_list,
		selected_investor=selected_investor,
		portfolio_count=portfolio_count,
		confirmation=confirmation,
		message=message
	)
	return render_template("manage_investor.html", **context)


@app.route('/add_holdings', methods=['GET'])
def add_holdings():
	"""
	Page for adding new holdings to portfolios
	"""
	# Get all investors for the first dropdown
	investors_query = "SELECT investor_id, company_name FROM investor ORDER BY investor_id"
	cursor = g.conn.execute(text(investors_query))
	investors_list = []
	for result in cursor:
		investors_list.append({'investor_id': result[0], 'company_name': result[1]})
	cursor.close()
	
	# Get selected investor if provided
	selected_investor_id = request.args.get('investor_id', '')
	
	# Get portfolios for selected investor
	portfolios_list = []
	if selected_investor_id:
		portfolios_query = "SELECT portfolio_id, total_value, creation_date FROM portfolio WHERE investor_id = :investor_id ORDER BY portfolio_id"
		cursor = g.conn.execute(text(portfolios_query), {"investor_id": selected_investor_id})
		for result in cursor:
			portfolios_list.append({
				'portfolio_id': result[0],
				'total_value': result[1],
				'creation_date': result[2]
			})
		cursor.close()
	
	# Get all stocks for the stock dropdown
	stocks_query = "SELECT stock_id, ticker, sector FROM stock ORDER BY ticker"
	cursor = g.conn.execute(text(stocks_query))
	stocks_list = []
	for result in cursor:
		stocks_list.append({
			'stock_id': result[0],
			'ticker': result[1],
			'sector': result[2]
		})
	cursor.close()
	
	# Get confirmation messages
	confirmation = request.args.get('confirmation', '')
	message = request.args.get('message', '')
	
	context = dict(
		investors=investors_list,
		portfolios=portfolios_list,
		stocks=stocks_list,
		selected_investor_id=selected_investor_id,
		confirmation=confirmation,
		message=message
	)
	return render_template("add_holdings.html", **context)


# Route to display all stocks
@app.route('/stocks')
def stocks():
	"""
	Display all stocks from the database
	"""
	# Query to get all stocks
	select_query = "SELECT * FROM stock"
	cursor = g.conn.execute(text(select_query))
	
	stocks_list = []
	for result in cursor:
		stocks_list.append(result)
	cursor.close()
	
	# Pass the stocks data to the template
	context = dict(stocks=stocks_list)
	return render_template("stocks.html", **context)


# Route to display all investors
@app.route('/investors')
def investors():
	"""
	Display all investors from the database
	"""
	# Query to get all investors
	select_query = "SELECT * FROM investor"
	cursor = g.conn.execute(text(select_query))
	
	investors_list = []
	for result in cursor:
		investors_list.append(result)
	cursor.close()
	
	# Pass the investors data to the template
	context = dict(investors=investors_list)
	return render_template("investors.html", **context)


# Route to display all transactions
@app.route('/transactions')
def transactions():
	"""
	Display all transactions from the database
	"""
	# Query to get all transactions
	select_query = "SELECT * FROM transaction"
	cursor = g.conn.execute(text(select_query))
	
	transactions_list = []
	for result in cursor:
		transactions_list.append(result)
	cursor.close()
	
	# Pass the transactions data to the template
	context = dict(transactions=transactions_list)
	return render_template("transactions.html", **context)


# Route to display all holdings
@app.route('/holdings')
def holdings():
	"""
	Display all holdings from the database
	"""
	# Query to get all holdings
	select_query = "SELECT * FROM holdings"
	cursor = g.conn.execute(text(select_query))
	
	holdings_list = []
	for result in cursor:
		holdings_list.append(result)
	cursor.close()
	
	# Pass the holdings data to the template
	context = dict(holdings=holdings_list)
	return render_template("holdings.html", **context)


# Route to display all portfolios
@app.route('/portfolios')
def portfolios():
	"""
	Display all portfolios from the database
	"""
	# Query to get all portfolios
	select_query = "SELECT * FROM portfolio"
	cursor = g.conn.execute(text(select_query))
	
	portfolios_list = []
	for result in cursor:
		portfolios_list.append(result)
	cursor.close()
	
	# Pass the portfolios data to the template
	context = dict(portfolios=portfolios_list)
	return render_template("portfolios.html", **context)


# Route to display all risk metrics
@app.route('/risk_metrics')
def risk_metrics():
	"""
	Display all risk metrics from the database
	"""
	# Query to get all risk metrics
	select_query = "SELECT * FROM risk_metrics"
	cursor = g.conn.execute(text(select_query))
	
	risk_metrics_list = []
	for result in cursor:
		risk_metrics_list.append(result)
	cursor.close()
	
	# Pass the risk metrics data to the template
	context = dict(risk_metrics=risk_metrics_list)
	return render_template("risk_metrics.html", **context)


# Route to display all macro data
@app.route('/macro_data')
def macro_data():
	"""
	Display all macro data from the database
	"""
	# Query to get all macro data
	select_query = "SELECT * FROM daily_macro_data"
	cursor = g.conn.execute(text(select_query))
	
	macro_data_list = []
	for result in cursor:
		macro_data_list.append(result)
	cursor.close()
	
	# Pass the macro data to the template
	context = dict(macro_data=macro_data_list)
	return render_template("macro_data.html", **context)


# Route to display all stock prices
@app.route('/stock_prices')
def stock_prices():
	"""
	Display all stock prices from the database
	"""
	# Query to get all stock prices
	select_query = "SELECT * FROM stock_price"
	cursor = g.conn.execute(text(select_query))
	
	stock_prices_list = []
	for result in cursor:
		stock_prices_list.append(result)
	cursor.close()
	
	# Pass the stock prices data to the template
	context = dict(stock_prices=stock_prices_list)
	return render_template("stock_prices.html", **context)


# Route to display all ESG scores
@app.route('/esg_scores')
def esg_scores():
	"""
	Display all ESG scores from the database
	"""
	# Query to get all ESG scores
	select_query = "SELECT * FROM esg_score"
	cursor = g.conn.execute(text(select_query))
	
	esg_scores_list = []
	for result in cursor:
		esg_scores_list.append(result)
	cursor.close()
	
	# Pass the ESG scores data to the template
	context = dict(esg_scores=esg_scores_list)
	return render_template("esg_scores.html", **context)


# Route to display top investors by P&L
@app.route('/top_investors')
def top_investors():
	"""
	Display investors ranked by profit/loss on their holdings
	Calculates P&L as: (current_price - average_price) * holding_count
	"""
	# Query to calculate P&L for each investor
	select_query = """
		SELECT 
			i.investor_id,
			i.company_name,
			COALESCE(SUM((latest_prices.daily_price - h.average_price) * h.holding_count), 0) as total_pnl,
			COUNT(h.stock_id) as num_holdings
		FROM investor i
		LEFT JOIN portfolio p ON i.investor_id = p.investor_id
		LEFT JOIN holdings h ON p.portfolio_id = h.portfolio_id
		LEFT JOIN (
			SELECT DISTINCT ON (stock_id) stock_id, daily_price
			FROM stock_price
			ORDER BY stock_id, price_date DESC
		) latest_prices ON h.stock_id = latest_prices.stock_id
		GROUP BY i.investor_id, i.company_name
		ORDER BY total_pnl DESC
	"""
	cursor = g.conn.execute(text(select_query))
	
	investors_list = []
	for result in cursor:
		investors_list.append(result)
	cursor.close()
	
	# Pass the investors data to the template
	context = dict(investors=investors_list)
	return render_template("top_investors.html", **context)


# Route to display top ESG portfolios with risk metrics
@app.route('/esg-stocks')
def esg_stocks():
	"""
	Display portfolios ranked by average ESG score with risk metrics
	Shows correlation between sustainability and risk-adjusted returns
	"""
	# Query joins Portfolio, Holdings, ESG_Score, and Risk_Metrics tables
	select_query = """
		SELECT p.portfolio_id,
			ROUND(AVG(e.esg_score), 2) AS avg_esg_score,
			r.sharpe_ratio,
			r.beta
		FROM Portfolio p
		JOIN Holdings h ON p.portfolio_id = h.portfolio_id
		JOIN ESG_Score e ON h.stock_id = e.stock_id
		JOIN Risk_Metrics r ON p.portfolio_id = r.portfolio_id
		GROUP BY p.portfolio_id, r.sharpe_ratio, r.beta
		ORDER BY avg_esg_score DESC
	"""
	cursor = g.conn.execute(text(select_query))
	
	portfolios_list = []
	for result in cursor:
		portfolios_list.append(result)
	cursor.close()
	
	# Pass the portfolios data to the template
	context = dict(portfolios=portfolios_list)
	return render_template("esg-stocks.html", **context)


# Route to display best buy transactions by unrealized P&L
@app.route('/best_buys')
def best_buys():
	"""
	Display buy transactions ranked by unrealized gain/loss
	Calculates unrealized P&L as: (current_price - purchase_price) * unit_number
	"""
	# Query joins Transaction, Stock, and Stock_Price tables
	select_query = """
		SELECT 
			t.investor_id,
			s.ticker,
			t.unit_price AS purchase_price,
			sp.daily_price AS current_price,
			ROUND((sp.daily_price - t.unit_price) * t.unit_number, 2) AS unrealized_gain
		FROM Transaction t
		JOIN Stock s ON t.stock_id = s.stock_id
		JOIN (
			SELECT stock_id, daily_price
			FROM stock_price
			WHERE (stock_id, price_date) IN (
				SELECT stock_id, MAX(price_date)
				FROM stock_price
				GROUP BY stock_id
			)
		) sp ON s.stock_id = sp.stock_id
		WHERE t.transaction_type = 'buy'
		ORDER BY unrealized_gain DESC
	"""
	cursor = g.conn.execute(text(select_query))
	
	transactions_list = []
	for result in cursor:
		transactions_list.append(result)
	cursor.close()
	
	# Pass the transactions data to the template
	context = dict(transactions=transactions_list)
	return render_template("best_buys.html", **context)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	company_name = request.form.get('company_name', '').strip()
	
	# Validate that company name is not empty
	if not company_name:
		return redirect('/new_investor?confirmation=error&company_name=')
	
	# Query for all investor IDs to find the maximum numeric part
	max_id_query = "SELECT investor_id FROM investor ORDER BY investor_id DESC LIMIT 1"
	cursor = g.conn.execute(text(max_id_query))
	result = cursor.fetchone()
	cursor.close()
	
	# Extract numeric part from investor_id (format: INV###)
	# Get the max number and add 1 (handle case where table is empty)
	if result and result[0]:
		# Extract numeric part from format like 'INV013'
		numeric_part = int(result[0].replace('INV', ''))
		new_number = numeric_part + 1
	else:
		new_number = 1
	
	# Format the new investor_id with leading zeros (e.g., INV014)
	new_investor_id = f'INV{new_number:03d}'
	
	# Insert the new investor
	params = {
		"investor_id": new_investor_id,
		"company_name": company_name
	}
	insert_query = "INSERT INTO investor(investor_id, company_name) VALUES (:investor_id, :company_name)"
	g.conn.execute(text(insert_query), params)
	
	# Now create a portfolio for this investor
	# Query for all portfolio IDs to find the maximum numeric part
	max_portfolio_query = "SELECT portfolio_id FROM portfolio ORDER BY portfolio_id DESC LIMIT 1"
	cursor = g.conn.execute(text(max_portfolio_query))
	portfolio_result = cursor.fetchone()
	cursor.close()
	
	# Extract numeric part from portfolio_id (format: PORT###)
	# Get the max number and add 1 (handle case where table is empty)
	if portfolio_result and portfolio_result[0]:
		# Extract numeric part from format like 'PORT013'
		portfolio_numeric = int(portfolio_result[0].replace('PORT', ''))
		new_portfolio_number = portfolio_numeric + 1
	else:
		new_portfolio_number = 1
	
	# Format the new portfolio_id with leading zeros (e.g., PORT014)
	new_portfolio_id = f'PORT{new_portfolio_number:03d}'
	
	# Get the current date from the system, or use default if not available
	try:
		creation_date = date.today().strftime('%Y-%m-%d')
	except:
		creation_date = '2025-11-12'
	
	# Insert the new portfolio with initial total_value of 0 and current date
	insert_portfolio_query = """
		INSERT INTO portfolio(portfolio_id, investor_id, total_value, creation_date) 
		VALUES (:portfolio_id, :investor_id, :total_value, :creation_date)
	"""
	g.conn.execute(text(insert_portfolio_query), {
		"portfolio_id": new_portfolio_id,
		"investor_id": new_investor_id,
		"total_value": 0,
		"creation_date": creation_date
	})
	
	g.conn.commit()
	
	# Redirect with confirmation message including portfolio info
	return redirect(f'/new_investor?confirmation=success&investor_id={new_investor_id}&company_name={company_name}&portfolio_id={new_portfolio_id}')


@app.route('/update_investor', methods=['POST'])
def update_investor():
	"""
	Update an investor's company name
	"""
	investor_id = request.form.get('investor_id', '').strip()
	new_company_name = request.form.get('company_name', '').strip()
	
	# Validate inputs
	if not investor_id or not new_company_name:
		return redirect('/manage_investor?confirmation=error&message=Invalid input')
	
	# Update the investor
	update_query = "UPDATE investor SET company_name = :company_name WHERE investor_id = :investor_id"
	params = {
		"investor_id": investor_id,
		"company_name": new_company_name
	}
	g.conn.execute(text(update_query), params)
	g.conn.commit()
	
	# Redirect with success message
	return redirect(f'/manage_investor?investor_id={investor_id}&confirmation=success&message=Company name updated successfully')


@app.route('/delete_investor', methods=['POST'])
def delete_investor():
	"""
	Delete an investor and their associated portfolios
	"""
	investor_id = request.form.get('investor_id', '').strip()
	
	# Validate input
	if not investor_id:
		return redirect('/manage_investor?confirmation=error&message=Invalid investor ID')
	
	try:
		# First, get all portfolio IDs for this investor
		portfolio_query = "SELECT portfolio_id FROM portfolio WHERE investor_id = :investor_id"
		cursor = g.conn.execute(text(portfolio_query), {"investor_id": investor_id})
		portfolio_ids = [row[0] for row in cursor]
		cursor.close()
		
		# Delete holdings for each portfolio
		for portfolio_id in portfolio_ids:
			delete_holdings_query = "DELETE FROM holdings WHERE portfolio_id = :portfolio_id"
			g.conn.execute(text(delete_holdings_query), {"portfolio_id": portfolio_id})
		
		# Delete risk metrics for each portfolio
		for portfolio_id in portfolio_ids:
			delete_risk_query = "DELETE FROM risk_metrics WHERE portfolio_id = :portfolio_id"
			g.conn.execute(text(delete_risk_query), {"portfolio_id": portfolio_id})
		
		# Delete portfolios for this investor
		delete_portfolio_query = "DELETE FROM portfolio WHERE investor_id = :investor_id"
		g.conn.execute(text(delete_portfolio_query), {"investor_id": investor_id})
		
		# Delete transactions for this investor
		delete_transactions_query = "DELETE FROM transaction WHERE investor_id = :investor_id"
		g.conn.execute(text(delete_transactions_query), {"investor_id": investor_id})
		
		# Finally, delete the investor
		delete_investor_query = "DELETE FROM investor WHERE investor_id = :investor_id"
		g.conn.execute(text(delete_investor_query), {"investor_id": investor_id})
		
		g.conn.commit()
		
		# Redirect with success message
		return redirect('/manage_investor?confirmation=success&message=Investor and associated data deleted successfully')
	
	except Exception as e:
		g.conn.rollback()
		return redirect(f'/manage_investor?confirmation=error&message=Error deleting investor: {str(e)}')


@app.route('/submit_holdings', methods=['POST'])
def submit_holdings():
	"""
	Add new holdings to a portfolio
	"""
	investor_id = request.form.get('investor_id', '').strip()
	portfolio_id = request.form.get('portfolio_id', '').strip()
	stock_id = request.form.get('stock_id', '').strip()
	average_price = request.form.get('average_price', '').strip()
	holding_count = request.form.get('holding_count', '').strip()
	
	# Validate all required fields are present
	if not all([investor_id, portfolio_id, stock_id, average_price, holding_count]):
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=All fields are required')
	
	# Validate and convert average_price to float
	try:
		average_price_float = float(average_price)
	except ValueError:
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=Average price must be a numeric value')
	
	# Validate and convert holding_count to int (round down if float)
	try:
		holding_count_float = float(holding_count)
		holding_count_int = int(holding_count_float)  # This rounds down automatically
	except ValueError:
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=Holding count must be a numeric value')
	
	# Check if this holding already exists (stock_id, portfolio_id is primary key)
	check_query = "SELECT COUNT(*) FROM holdings WHERE stock_id = :stock_id AND portfolio_id = :portfolio_id"
	cursor = g.conn.execute(text(check_query), {"stock_id": stock_id, "portfolio_id": portfolio_id})
	exists = cursor.fetchone()[0] > 0
	cursor.close()
	
	if exists:
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=This stock already exists in the selected portfolio')
	
	try:
		# Get the most current stock price for the selected stock
		price_query = """
			SELECT daily_price 
			FROM stock_price 
			WHERE stock_id = :stock_id 
			ORDER BY price_date DESC 
			LIMIT 1
		"""
		cursor = g.conn.execute(text(price_query), {"stock_id": stock_id})
		price_result = cursor.fetchone()
		cursor.close()
		
		if not price_result or price_result[0] is None:
			return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=No price data found for selected stock')
		
		current_stock_price = float(price_result[0])
		
		# Calculate the value to add to portfolio: holding_count * current_stock_price
		value_to_add = holding_count_int * current_stock_price
		
		# Insert the new holding
		insert_query = """
			INSERT INTO holdings(stock_id, portfolio_id, average_price, holding_count) 
			VALUES (:stock_id, :portfolio_id, :average_price, :holding_count)
		"""
		g.conn.execute(text(insert_query), {
			"stock_id": stock_id,
			"portfolio_id": portfolio_id,
			"average_price": average_price_float,
			"holding_count": holding_count_int
		})
		
		# Update the portfolio's total_value by adding the new holding value
		update_portfolio_query = """
			UPDATE portfolio 
			SET total_value = total_value + :value_to_add 
			WHERE portfolio_id = :portfolio_id
		"""
		g.conn.execute(text(update_portfolio_query), {
			"value_to_add": value_to_add,
			"portfolio_id": portfolio_id
		})
		
		g.conn.commit()
		
		# Redirect with success message including the added value
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=success&message=Holdings added successfully! Portfolio value increased by ${value_to_add:.2f}')
	
	except Exception as e:
		g.conn.rollback()
		return redirect(f'/add_holdings?investor_id={investor_id}&confirmation=error&message=Error adding holdings: {str(e)}')


@app.route('/login')
def login():
	abort(401)
	# Your IDE may highlight this as a problem - because no such function exists (intentionally).
	# This code is never executed because of abort().
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
