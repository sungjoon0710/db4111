
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


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


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
