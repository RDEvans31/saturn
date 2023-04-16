import pandas as pd
import numpy as np
import price_data as price
import ccxt
import chart
from datetime import datetime
import pickle

# import the data from the csv file
price_data_csv = pd.read_csv("data/Bitfinex_ETHUSD_1h.csv")

class Context: 
    def __init__(self, price_data, calculation_window, trade_side, context_window=10):
        self.price_data = price_data
        self.calculation_window = calculation_window
        self.context_window = context_window
        self.context_sequence = self.calculate_context_sequence()
        self.trade_side = trade_side
    
    def calculate_context_sequence(self):
        self.context_window
        current_price = price_data.iloc[-1]['open']
        moving_average_channel = chart.ma_channel(price_data, self.calculation_window)
        # ratio between last 10 open prices and the corresponding upper and lower bounds of the moving average channel
        open_prices = price_data.iloc[-self.context_window:]['open']
        upper_bounds = moving_average_channel.iloc[-self.context_window:]['high']
        lower_bounds = moving_average_channel.iloc[-self.context_window:]['low']
        open_upper_ratio = (open_prices-upper_bounds)/(upper_bounds-lower_bounds)
        open_lower_ratio = (open_prices-lower_bounds)/(upper_bounds-lower_bounds)
        upper_lower__open_ratio = (upper_bounds-lower_bounds)/(open_prices)
        normalised_atr = chart.get_normalised_atr(price_data, self.calculation_window).iloc[-self.context_window:]
        # print all lengths 
        context_sequence = np.array([open_upper_ratio, open_lower_ratio, upper_lower__open_ratio, normalised_atr])
        return context_sequence.T

    def get_context_sequence(self):
        trade = 0
        if self.trade_side == 'long':
            trade = 1
        return (trade,self.context_sequence)
        


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
    contextual_data = []
    for i, row in price_data.iterrows():
        print(f'Processing: {(i/len(price_data))*100:.2f}%', end='\r')
        if i>ma_channel_window+no_opens:
            
            # Get the open, high, low, and close prices
            current_time = row['unix']
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
                trade_context = Context(current_price_data, ma_channel_window, position)

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
                trades.append((pd.to_datetime(timestamp, unit='ms'), pd.to_datetime(current_time, unit='ms'),position, open_price, entry, balance, prev_balance<balance, open_price<channel.iloc[-1]['high'] and open_price>entry, open_price>channel.iloc[-1]['low']and open_price<entry))
                contextual_data.append((trade_context.get_context_sequence(), prev_balance<balance))
                timestamp=None
                position = None
                
        # if balance<=0:
        #     break

    trades_df = pd.DataFrame(trades, columns=['timestamp', 'timestamp_exit','side', 'exit', 'entry', 'balance', 'win', 'open_below_channel_high', 'open_above_channel_low'])
    print(trades_df)
    win_rate = trades_df['win'].sum()/len(trades_df)
    print(f"Win rate: {win_rate:.2f}")
    # Calculate the overall performance of the strategy
    roi = (balance - 1000.0) / 1000.0
    print(f"ROI: {roi:.2f}")
    return balance, trades_df, contextual_data

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
balance, trades_df, training_data = backtest_strategy(price_data, 4, 128)
with open('data/mean_reversion_training_data.pkl', 'wb') as f:
    pickle.dump(training_data, f)