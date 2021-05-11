import requests
import pandas as pd
import json
import config
import sys
import time
import numpy as np
import pretty_errors
# 3rd party
from tda import auth, client
from flask import Flask, render_template
from colour import Color
# local
from fundamentals import *
from indicators import *


app = Flask(__name__)

def authenticate():
    pass

def price_history_period(ticker, period='year'):
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

# STOCK FUNDAMENTALS
@app.route("/<ticker>")
def get_fundamentals(ticker):
    data = c.search_instruments(ticker, projection=client.Client.Instrument.Projection.FUNDAMENTAL)
    assert data.status_code == 200, data.raise_for_status()       # Not sure what this does
    data = data.json()         # Original  data is of type "<class 'requests.models.Response'>"
    fundamentals = data[ticker]['fundamental']
    keys = data[ticker]['fundamental'].keys()  # Gets the categories
    return render_template('fundamentals.html', ticker=ticker, fund=fundamentals)

 #REAL BODIES
@app.route("/<ticker>/real_body")
def real_body(ticker):
    """ Displays real_bodies """
    max_real_bodies = indicators.real_body_candle(ticker=ticker, period='year', bull=True, iterations=5)
    return render_template('real_body.html', ticker=ticker, max_real_bodies=max_real_bodies, iterations=5, period='year')

# RISING AND FALLING WINDOWS
@app.route("/<ticker>/windows")
def get_windows(ticker):
    """ Rising and falling windows in past 1 year """
    rising_windows, falling_windows, max_support, max_resistance=indicators.windows(ticker=ticker, period='year')
    return render_template('windows.html', ticker=ticker, period='year', rising_windows=rising_windows, falling_windows=falling_windows,
                                                            max_support=max_support, max_resistance=max_resistance)
# Define a threshold?
@app.route("/scan_windows")
def near_windows():
    """Return tickers from given list of tickers that have current price near support/resistance"""
    near_support, near_resistance = indicators.scan_tickers_near_support_resistance(tickers)
    return render_template('near_windows_2.html', near_support=near_support, near_resistance=near_resistance)

#----------------------------- MAIN-------------------------------------------
# Authentication
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path='/Users/Evan/Documents/trading/chromedriver') as driver:
        # authenticate from token config.py file
        c = auth.client_from_login_flow(driver, config.api_key, config.redirect_uri, config.token_path)

# Start thinking of user input in terminal. Ask terminal for input
# i = sys.argv.index('server:app')
# ticker = sys.argv[i+1]      # first argument = ticker
# gunicorn --threads 4 -b 0.0.0.0:5000 --access-logfile server.log server:app

df = pd.read_csv('Watchlist.csv')
tickers = df['Symbol'].tolist()
#tickers = ['TDOC', 'LULU', 'CRWD', 'CGC', 'SPOT', 'FTCH', 'NVDA', 'AMD', 'CRM', 'DOCU']
print(tickers)
app.run(host='0.0.0.0', port=5000)
