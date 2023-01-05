import pandas as pd
import numpy as np
import price_data as price
import ccxt
import chart
from datetime import datetime

# import requests

# # Set the URL for the API endpoint
# url = "https://min-api.cryptocompare.com/data/v2/histohour"

# # Set the parameters for the API request
# params = {
#     "fsym": "ETH",
#     "tsym": "USD",
#     "limit": 2000,  # Set the maximum number of data points to retrieve
#     "aggregate": 1  # Set the aggregation period to 1 hour
# }

# # Make the API request
# response = requests.get(url, params=params)

# # Check the status code of the response to ensure the request was successful
# if response.status_code == 200:
#     # Retrieve the data from the response
#     data = response.json()
    
#     # Access the data points in the 'Data' field of the response
#     data_points = data["Data"]["Data"]
    
#     # Print the first data point
#     print(data_points[0])
# else:
#     # Print an error message if the request was unsuccessful
#     print("An error occurred:", response.text)


def identify_trend_variable(price_data, channel_period, no_opens=5, minute=False): #using moving average channel
    channel=chart.ma_channel(price_data,channel_period)
    
    upper_bound=channel.iloc[-no_opens:]['high']
    lower_bound=channel.iloc[-no_opens:]['low']

    if minute:
        opens=price_data.iloc[-no_opens:]['close']
    else:
        opens=price_data.iloc[-no_opens:]['open']

    if (opens>upper_bound).all():
        return 'uptrend'
    elif (opens<lower_bound).all():
        return 'downtrend'
    else:
        return 'neutral'

price_data = price.get_price_data('1m', symbol='ETH/USD')

def backtest_strategy(price_data, no_opens, ma_channel_window):

    balance = 1000.0
    position = None
    # ma_channel_window = 24
    # no_opens = 2
    trades =[]
    for i, row in price_data.iterrows():

        if i>ma_channel_window+no_opens:
            # Get the open, high, low, and close prices
            open_price = row["open"]
            high_price = row["high"]
            low_price = row["low"]
            close_price = row["close"]

            current_price_data = price_data.iloc[0:i]

            channel = chart.ma_channel(current_price_data, ma_channel_window)
            trend = identify_trend_variable(current_price_data,ma_channel_window,no_opens)
            # entry conditions
            if position == None:

                if trend == 'uptrend':
                    position = "short"
                    entry = open_price
                elif trend == 'downtrend':
                    position = "long"
                    entry = open_price

            # exit condition
            # essentially mean reversion
            # if the open_price is above the entry price and below the top of the channel, or the open_price is below the entry price and above the bottom of the channel, exit
            elif (open_price<channel.iloc[-1]['high'] and open_price>entry) or (open_price>channel.iloc[-1]['low'] and open_price<entry):            # calculate the profit/loss and add it to the balance
                # append trade to end of list
                prev_balance = balance
                if position == "long":
                    balance += 2*((open_price - entry)/entry)*balance
                elif position == "short":
                    # print(((entry - open_price)/entry)*balance)
                    balance += 2*((entry - open_price)/entry)*balance
                trades.append((position, open_price, entry, balance, prev_balance<balance, open_price<channel.iloc[-1]['high'] and open_price>entry, open_price>channel.iloc[-1]['low']and open_price<entry))
                position = None
                


    trades_df = pd.DataFrame(trades, columns=['side', 'exit', 'entry', 'balance', 'win', 'open_below_channel_high', 'open_above_channel_low'])
    win_rate = trades_df['win'].sum()/len(trades_df)
    print(f"Win rate: {win_rate:.2f}")
    # Calculate the overall performance of the strategy
    roi = (balance - 1000.0) / 1000.0
    print(f"ROI: {roi:.2f}")
    return balance, trades_df

ma_channel_period = [20, 21, 22, 23, 24]
no_opens = [2]
results = []
# for ma in ma_channel_period:
#     for no in no_opens:
#         print(f"ma_channel_period: {ma}, no_opens: {no}")
#         balance = backtest_strategy(price_data, no, ma)
#         results.append((ma, no, balance))

# results_df = pd.DataFrame(results, columns=['ma_channel_period', 'no_opens', 'balance'])
# results_df.sort_values(by='balance', ascending=False)
# print(results_df)

balance, trades_df = backtest_strategy(price_data, 2, 23)

# only show the rows from trades_df where win is false
losses = trades_df[trades_df['win']==False]
wins = trades_df[trades_df['win']==True]
# calculate the average loss by taking the differnce between the entry and exit price and dividing by the entry price
loss = abs(losses['entry']-losses['exit'])/losses['entry']
win = abs(wins['entry']-wins['exit'])/wins['entry']

print(win.mean()/loss.mean())