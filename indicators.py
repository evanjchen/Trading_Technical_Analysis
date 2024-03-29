import json
import datetime as dt
import numpy as np
import wrapper
import pretty_errors
from tda import auth, client


""" NOTE: the first lines of code for loading a stock's data is repetetive """
""" NOTE: Print results to html??"""
    #response = c.search_instruments(['AMD', 'SQ'], c.Instrument.Projection.FUNDAMENTAL)

def to_date(timestamp):
    """converts the timestamp to a date"""
    date = dt.datetime.fromtimestamp(timestamp/1000)
    return date.strftime("%m/%d/%y")


def real_body_candle(ticker, period='year', bull=True, iterations=1):
    """Finds top n real body daily candles - 1 year history.
    Specify the following: period, bull, iterations
    Returns a list of dictionaries with keys: """
    #  Calls function in wrapper.py to get Price history data in dictionary form
    data = wrapper.price_history_period(ticker, period)
    # empty list of dictionaries based on iterations
    max_bodies = [{} for x in range(iterations)]
    color = 'GREEN'
    if bull == False: color = "RED"
    for i in range(iterations):
        real_bodies = [record.get('close') - record.get('open') for record in data['candles']]
        # RED or GREEN candle - gets the maximum difference between open and close
        if(bull): max_real_body = max(real_bodies)
        else:     max_real_body = min(real_bodies)
        # Gets which day it occurs
        date_index = real_bodies.index(max_real_body)
        open_price =  data['candles'][date_index].get('open')
        close_price = data['candles'][date_index].get('close')
        change = np.round(max_real_body/open_price * 100, 2)
        date_occurred = to_date(data['candles'][date_index].get('datetime'))

        # Populate list of dictionaries
        max_bodies[i]['date'] = date_occurred
        max_bodies[i]['real_body'] = np.round(max_real_body, 2)
        max_bodies[i]['open'] = open_price
        max_bodies[i]['close'] = close_price
        max_bodies[i]['change'] = change

        print("[Iteration",  str(i+1) +"]" )
        print("DATE OCCURRED:", date_occurred)
        print("REAL BODY (" + color + "):", np.round(max_real_body, 2))
        print("CHANGE:", change)
        print("OPEN:",  open_price)
        print("CLOSE:", close_price)
        print("\n")
        # Remove the list element to get next highest body
        data['candles'].pop(date_index)
    return max_bodies

def volume_Screener(tickers, sd=3):
    """default standard deviation = 3 for an array of stocks for past 1 month"""
    """ Display commas"""
    # Begin iterating through all tickers in array

    # VOlume screener will be used broadly
    # BPossibly make a nested if-statement for daily.
    # Maybe create dictionary instead? {key = candle: values dictionary}]

    for ticker in tickers:
        #  Calls function in wrapper.py to get Price history in dictionary form
        data = wrapper.price_history_period(ticker, period='month')
        high_volume = {}
        # list of dictionaries for each day's candle
        daily_candles = data['candles']
        daily_volumes = [day.get('volume') for day in daily_candles]
        mean = int(np.mean(daily_volumes))
        std = int(np.std(daily_volumes))
        daily_deviations = [np.round((volume-mean)/std, 3) for volume in daily_volumes]
        # Index of the daily_deviations represents index in daily_candles
        print("TICKER:", ticker)
        print("AVG VOLUME (3 months): " +  f"{mean:,d}")
        print("Standard Deviation: " + f"{std:,d}" + "\n")

        for i, deviation in enumerate(daily_deviations):
            if deviation > sd:
                date = to_date(daily_candles[i].get('datetime'))
                high_volume[date] = deviation
        for k, v in high_volume.items():
            print("Date occurred:", k)
            print("Standard deviations above mean:", v, "\n")

def call_chain(tick, strike, start_date, end_date):
    """dates in YYYY-MM-DD format"""
    start = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    end = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
    # Maybe we can ask user for input? 1-12 for months for start and end months?
    options = c.get_option_chain('AMD', contract_type = c.Options.ContractType.CALL,
    strike = strike, strike_from_date = start, strike_to_date = end)
    print(json.dumps(options.json(), indent = 4))


def windows(ticker, period='year'):
    "Gives support levels based on rising and falling windows "
    data = wrapper.price_history_period(ticker, period)
    candles = data['candles']
    rising_windows, falling_windows = [], []
    max_support, max_resistance = None, None
    # Gets date, high of first day and low of next day
    for day_1, day_2 in zip(candles[:-1], candles[1:]):
        # Rising windows: (Date, support, gap-up)
        if day_2.get('low') > day_1.get('high'):
            date_occurred = to_date(day_1.get('datetime'))
            gap_up = '{:.2f}'.format(np.round(day_2.get('low') - day_1.get('high'), 2))
            support = '{:.2f}'.format(np.round(day_1.get('high'), 2))
            rising_windows.append((date_occurred, support, gap_up))
        # Falling windows: (Date, support, gap-down)
        if day_1.get('low') > day_2.get('high'):
            date_occurred = to_date(day_1.get('datetime'))
            gap_down = '{:.2f}'.format(np.round(day_1.get('low') - day_2.get('high'), 2))
            resistance = '{:.2f}'.format(np.round(day_1.get('low'), 2))
            falling_windows.append((date_occurred, resistance, gap_down))
    max_support =    max([float(window[1]) for window in rising_windows])
    max_resistance = max([float(window[1]) for window in falling_windows])
    return rising_windows, falling_windows, max_support, max_resistance

# ISSUE: TOO MANY REQUESTS
def scan_tickers_near_support_resistance(tickers):
    """Return tickers from given list of tickers that have current price near support/resistance
    -------- Define Threshold ------Edit to add most recent support/resistance"""
    # NOTE:: BASING ON MOST RECENT SUPPORT/RESISTANCE OR MAX
    # ----------CURRENTLY NEXT TO MAX_SUPPORT----------------------
    # tickers = wrapper.get_sp500_tickers()
    near_support, near_resistance = {}, {}
    threshold = 2    # Define threshold
    # Need to make dictionary with keys: tickers, current_price, max_support, max_resistance, recent, support, recent_resistance
    # Get following: (Max_support, date), (Max_resist, date), (Recent_support, date), (Recent_resist, date)
    for ticker in tickers:
        print(ticker)
        rising_windows, falling_windows, max_support, max_resistance = windows(ticker, period='year')   # Call above function
        most_rcnt_support = rising_windows[-1]          # gets tuple of date, support, nominal
        most_rcnt_resistance = falling_windows[-1]      # gets tuple of date, resistance, nominal
        current_price = wrapper.get_current_price(ticker)
        # base by threshold % points
        if abs((current_price - float(most_rcnt_support[1]))/current_price) <= threshold/100:
            near_support[ticker] = {'last_price' : current_price,
                                    'most_rcnt_support_date' : most_rcnt_support[0],
                                    'most_rcnt_support_lvl' : float(most_rcnt_support[1]),
                                    'most_rcnt_resist_date' : most_rcnt_resistance[0],
                                    'most_rcnt_resist_lvl' : float(most_rcnt_resistance[1]),
                                    'max_support': max_support,
                                    'max_resistance': max_resistance    }
        if abs((current_price - float(most_rcnt_resistance[1]))/current_price) <= threshold/100:
            near_resistance[ticker] = {'last_price' : current_price,
                                    'most_rcnt_support_date' : most_rcnt_support[0],
                                    'most_rcnt_support_lvl' : float(most_rcnt_support[1]),
                                    'most_rcnt_resist_date' : most_rcnt_resistance[0],
                                    'most_rcnt_resist_lvl' : float(most_rcnt_resistance[1]),
                                    'max_support': max_support          }
    return near_support, near_resistance
