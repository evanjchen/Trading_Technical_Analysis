from tda import auth, client
import requests
import json
import config
import sys
import time
from flask import Flask, render_template
from colour import Color
import numpy as np
import pretty_errors
# import other scripts
from fundamentals import *
from indicators import *


app = Flask(__name__)

def authenticate():
    pass

def price_history_period(ticker, period = 'year'):
    """Returns price_history data for a certain period"
    -----------------DEFAULT = 'year'--------------------
    year = 1 year (daily candle); month = 3 months(daily candle);  daily = 5 days (5 min candle)"""
    if period == 'year':
        price_history = c.get_price_history(ticker,
            period_type=client.Client.PriceHistory.PeriodType.YEAR,
            period=client.Client.PriceHistory.Period.ONE_YEAR,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
            frequency=client.Client.PriceHistory.Frequency.DAILY)
    if period == 'month':
        price_history = c.get_price_history(ticker,
            period_type=client.Client.PriceHistory.PeriodType.MONTH,
            period=client.Client.PriceHistory.Period.THREE_MONTHS,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
            frequency=client.Client.PriceHistory.Frequency.DAILY)
    if period == 'daily':
        price_history = c.get_price_history(ticker,
            period_type=client.Client.PriceHistory.PeriodType.DAY,
            period=client.Client.PriceHistory.Period.FIVE_DAYS,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
            frequency=client.Client.PriceHistory.Frequency.EVERY_FIVE_MINUTES)
    assert price_history.status_code == 200, price_history.raise_for_status()
    # Original  data is of type "<class 'requests.models.Response'>"
    return price_history.json()

def add_color(ticker):
    pass
    # colors = list(Color("red").range_to(Color("green"), 100))
    # for tweet in tweets:
    #     score = tweet['score']
    #     index = round((score + 1)*100/2) - 1
    #     tweet['color'] = colors[index]

@app.route("/favicon.ico")
def favicon():
    with open('icon2.png', 'rb') as f:
        return f.read()

@app.route("/<ticker>")
def get_fundamentals(ticker):
    # Only get the fundamnetals of interest
    data = c.search_instruments(ticker, projection = client.Client.Instrument.Projection.FUNDAMENTAL)
    assert data.status_code == 200, data.raise_for_status()       # Not sure what this does
    data = data.json()         # Original  data is of type "<class 'requests.models.Response'>"
    fundamentals = data[ticker]['fundamental']
    keys = data[ticker]['fundamental'].keys()  # Gets the categories
    return render_template('fundamentals.html', ticker = ticker, fund = fundamentals)

 # Need to pass in arguments to the URL
@app.route("/<ticker>/real_body")
def real_body(ticker):
    """ Displays real_bodies """
    max_real_bodies = indicators.real_body_candle(ticker = ticker, period = 'year',  bull = True, iterations = 5)
    return render_template('real_body.html', ticker = ticker, max_real_bodies = max_real_bodies, iterations = 5, period = 'year')



#----------------------------- MAIN-------------------------------------------

# start = time.time()
# Authentication
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path = '/Users/Evan/Documents/trading/chromedriver') as driver:
        # authenticate from token config.py file
        c = auth.client_from_login_flow(driver, config.api_key, config.redirect_uri, config.token_path)

# Start thinking of user input in terminal. Ask terminal for input
# i = sys.argv.index('server:app')
# ticker = sys.argv[i+1]      # first argument = ticker

# gunicorn --threads 4 -b 0.0.0.0:5000 --access-logfile server.log server:app

# end = time.time()
# print("TIME TO RUN:", end - start, "seconds")

# Remove this line of code after
app.run(host='0.0.0.0', port=5000)
