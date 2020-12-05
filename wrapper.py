from tda import auth, client
import json
import config       # stores token path and API key
import requests
import numpy as np
import pretty_errors

try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path = '/Users/Evan/Documents/trading/chromedriver') as driver:
        # authenticate from token config.py file
        c = auth.client_from_login_flow(driver, config.api_key, config.redirect_uri, config.token_path)

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
    assert price_history.status_code == 200, price_history.raise_for_status()       # Not sure what this does
    return price_history.json()


def get_fundamentals(ticker):
    # Only get the fundamnetals of interest
    data = c.search_instruments(ticker, projection = client.Client.Instrument.Projection.FUNDAMENTAL)
    assert data.status_code == 200, data.raise_for_status()       # Not sure what this does
    # data is of type "<class 'requests.models.Response'>"
    data = data.json()
    fundamentals = data[ticker]['fundamental']
    keys = data[ticker]['fundamental'].keys()
    print(keys)
    print(json.dumps(fundamentals, indent = 4))
    print(type(fundamentals))
    return fundamentals, keys
get_fundamentals('AMD')
