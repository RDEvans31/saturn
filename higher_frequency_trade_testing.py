import pandas as pd
import numpy as np
import price_data as price
import ccxt
import chart
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# import the data from the csv file
price_data_csv = pd.read_csv("data/FTX_ETHUSD_1h.csv")


def identify_trend_variable(price_data, channel_period, no_opens=5, minute=False): #using moving average channel
    channel=chart.ma_channel(price_data,channel_period)
    
    upper_bound=channel.iloc[-no_opens:]['high']
    lower_bound=channel.iloc[-no_opens:]['low']

    if minute:
        opens=price_data.iloc[-no_opens:]['close']
    else:
        opens=price_data.iloc[-no_opens:]['open']
    try:
        if (opens>upper_bound).all():
            return 'uptrend'
        elif (opens<lower_bound).all():
            return 'downtrend'
        else:
            return 'neutral'
    except:
        print(opens, upper_bound, lower_bound)

# price_data = price.get_price_data('1h', symbol='ETH/USD')
price_data = price.get_price_data(data=price_data_csv, timeframe='1h')
print(f"Datapoints: {len(price_data)/24}")
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
            if position == 'long':
                profit = (open_price - entry)/entry
            elif position == 'short':
                profit = (entry - open_price)/entry
            channel = chart.ma_channel(current_price_data, ma_channel_window)
            trend = identify_trend_variable(current_price_data,ma_channel_window,no_opens)
            # long_term_trend = identify_trend_variable(current_price_data,ma_channel_window,no_opens+1)

            # entry conditions 
            if position == None:
                # if long_term_trend != trend:
                if trend == 'uptrend': 
                    position = "short"
                    timestamp = row['unix']
                    entry = open_price
                elif trend == 'downtrend':
                    position = "long"
                    timestamp = row['unix']
                    entry = open_price
                

            # exit condition
            # essentially mean reversion
            # if the open_price is above the entry price and below the top of the channel, or the open_price is below the entry price and above the bottom of the channel, exit
            elif (open_price<channel.iloc[-1]['high'] and open_price>entry) or (open_price>channel.iloc[-1]['low'] and open_price<entry) or profit<-0.01:            # calculate the profit/loss and add it to the balance
                # append trade to end of list
                prev_balance = balance
                if position == "long":
                    balance += ((open_price - entry)/entry)*balance
                elif position == "short":
                    balance += ((entry - open_price)/entry)*balance
                trades.append((pd.to_datetime(timestamp, unit='ms'),position, open_price, entry, balance, prev_balance<balance, open_price<channel.iloc[-1]['high'] and open_price>entry, open_price>channel.iloc[-1]['low']and open_price<entry))
                timestamp=None
                position = None
                
        if balance<=0:
            break

    trades_df = pd.DataFrame(trades, columns=['timestamp','side', 'exit', 'entry', 'balance', 'win', 'open_below_channel_high', 'open_above_channel_low'])
    print(trades_df)
    win_rate = trades_df['win'].sum()/len(trades_df)
    print(f"Win rate: {win_rate:.2f}")
    # Calculate the overall performance of the strategy
    roi = (balance - 1000.0) / 1000.0
    print(f"ROI: {roi:.2f}")
    return balance, trades_df

# for hourly data it seems around 130 is the best option for the moving channel window
# for minute data it seems around 23 is the best option for the moving channel window

# fib_array = [5,8,13,21,34,55,89,144,233,377,610]
# ma_channel_period = [126,128,130,132]
# no_opens = [2,3,4,5,6]
# results = []
# for ma in ma_channel_period:
#     for no in no_opens:
#         balance, _ = backtest_strategy(price_data, no, ma)
#         print(f"ma_channel_period: {ma}, no_opens: {no}, final balance: {balance:.2f}")
#         results.append((ma, no, balance))

# results_df = pd.DataFrame(results, columns=['ma_channel_period', 'no_opens', 'balance'])
# results_df.sort_values(by='balance', ascending=True, inplace=True)
# print(results_df)

# print the timestamp of the first and last rows of price_data

balance, trades_df = backtest_strategy(price_data, 4, 128)
trades_df['rolling_balance'] = trades_df['value'].rolling(window=5).mean()
sns.scatterplot(x='timestamp', y='balance', data=trades_df)
sns.lineplot(x='timestamp', y='rolling_balance', data=trades_df, color='red', label='5 day rolling balance')
plt.show()
# # only show the rows from trades_df where win is false
# losses = trades_df[trades_df['win']==False]
wins = trades_df[trades_df['win']==True]
# # calculate the average loss by taking the differnce between the entry and exit price and dividing by the entry price
# loss = abs(losses['entry']-losses['exit'])/losses['entry']
win = abs(wins['entry']-wins['exit'])/wins['entry']
print(win.max())
# print(trades_df)
# print(win.mean()/loss.mean())