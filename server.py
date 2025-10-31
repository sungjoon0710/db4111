#!/usr/bin/env python3

"""
ESGTrader - Flask Web Application
A barebones Flask application that connects to PostgreSQL using SQLAlchemy.
No ORM features are used - only raw SQL queries.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

# Create the Flask application
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# IMPORTANT: Update this with your PostgreSQL credentials
# Format: postgresql://USER:PASSWORD@HOST/DATABASE
#
# Example: postgresql://myusername:mypassword@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2
#
DATABASEURI = "postgresql://USER:PASSWORD@HOST/DATABASE"

#
# Create the database engine
# We use NullPool to avoid issues with connections going away
#
engine = create_engine(DATABASEURI, pool_pre_ping=True, poolclass=NullPool)

#
# Example query: Test the connection
# You can uncomment this to test if your database connection works
#
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT 1"))
#     print(result.fetchone())


@app.before_request
def before_request():
    """
    This function is run before each request.
    We'll use it to set up a database connection for each request.
    """
    try:
        g.conn = engine.connect()
    except:
        print("Problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    This function is run after each request, to close the database connection.
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def index():
    """
    Main index page for ESGTrader
    """
    # Example of executing a query (commented out for now)
    # cursor = g.conn.execute(text("SELECT * FROM your_table LIMIT 10"))
    # results = cursor.fetchall()
    # cursor.close()
    
    return render_template("index.html")


@app.route('/stocks')
def stocks():
    """
    Display all stocks
    """
    # Example query to fetch all stocks (uncomment and modify when ready)
    # cursor = g.conn.execute(text("SELECT * FROM stocks"))
    # stocks = cursor.fetchall()
    # cursor.close()
    
    return render_template("stocks.html")


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

            python3 server.py

        Show the help text using:

            python3 server.py --help

        """
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

