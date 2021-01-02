import asyncio
from binance.client import Client
import ccxt
import requests
import user
import statistics
import time
import numpy as np
import pandas as pd

client=user.client
open_orders=client.futures_get_open_orders()

taapi_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InJvYmVydC5kLmV2YW5zMzEwMEBnbWFpbC5jb20iLCJpYXQiOjE2MDk1OTQwOTEsImV4cCI6NzkxNjc5NDA5MX0.8eaue13S_zhya0TS2mATlmI5SKQOM5ThEOPjzcQWg0g'

binance = ccxt.binance({
    'apiKey': 'HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK',
    'secret': '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4',
    'timeout': 30000,
    'enableRateLimit': True,
})

def convert_to_milliseconds(h): #enter time in hours
    return h*3600*1000

def get_current_time(exchange):
    return exchange.fetch_time()

# returns true if there are no more open orders for 
def symbol_open_orders(symbol):
    orders=list(filter(lambda x: x['symbol']==symbol, open_orders))
    if len(orders)==0:
        return True
    else:
        return False

# takes in the kline data and returns dataframe of timestamps and closing prices, could be adjusted for more price data
def get_closes(kline): 
    timestamps=list(map(lambda x: x[0], kline))
    timestamp_hr=np.array(list(map(lambda x: (x-timestamps[0])/3600000, timestamps)),dtype=float)
    closes=np.array(list(map(lambda x: x[4], kline)),dtype=float)

    return pd.DataFrame({'timestamp':timestamp_hr,'close':closes})

#these all rely on the above functions

def get_viable_trades_for_symbol(symbol):
    print('Checking:', symbol)
    if symbol_open_orders(symbol):
        trade_found=False

        if trade_found:
            return trade
        else:
            #print('Could not find trade for ', symbol)
            return
    else:
        #print("There are open orders for ", symbol)
        return 

def get_peaks(data):
    if len(data)>0:
        close_prices=get_closes(data)
        peaks=[]
        for i in range(1,len(data)-1):
            current_series=close_prices.iloc[i]
            if current_series["close"]>close_prices.iloc[i+1]["close"] and current_series["close"]>close_prices.iloc[i-1]["close"]:
                peaks.append([current_series["timestamp"],current_series["close"]]) #appends timestamp and price
        peaks_df=pd.DataFrame(data=peaks,columns=["timestamp","close"])
        return peaks_df
    else:
        return None

def get_troughs(data):
    if len(data)>0:
        close_prices=get_closes(data)
        troughs=[]
        for i in range(1,len(data)-1):
            current_series=close_prices.iloc[i]
            if current_series["close"]<close_prices.iloc[i+1]["close"] and current_series["close"]<close_prices.iloc[i-1]["close"]:
                troughs.append([current_series["timestamp"],current_series["close"]]) #appends timestamp and price
        troughs_df=pd.DataFrame(data=troughs,columns=["timestamp","close"])
        return troughs_df
    else:
        return None

#not fucntional
def get_stationary_points(interval,symbol):
    kline=None
    peaks=None
    troughs=None

    if kline!=None:
        
        peaks=get_peaks(kline)
        troughs=get_troughs(kline)
    
    stationary_points=pd.concat([peaks,troughs])
    stationary_points.sort_values(by=["timestamp"],inplace=True)

    return stationary_points
    
def identify_trend(symbol):
    time=binance.fetch_time()
    closes=get_closes(binance.fetchOHLCV(symbol,'1h',time-convert_to_milliseconds(24)))

    y=np.array(closes['close'],dtype=float)
    x=np.array(closes['timestamp'],dtype=float)

    dataframe=pd.DataFrame({'time':x,'price':y})
    print(dataframe)
    m, c=np.polyfit(x,y,1)
    print(m,c)

    if m>1.2:
        return 'BULL'
    if m<0.8:
        return 'BEAR'

def get_horizontal_lines(dataframe): #input dataframe comntaining peaks/troughs or both
    # rounding closing prices
    sup=dataframe["close"].max()
    inf=dataframe["close"].min()
    if dataframe["close"].min() < 1:   
        base=round((sup-inf)*0.05,2)
    else:
        base=round((sup-inf)*0.05)
    round_func=np.vectorize(lambda x: round(x))
    possible_lines=np.linspace(inf,sup, num=int((round(sup)-round(inf))/base))
    rounded_lines=round_func(possible_lines)
    #for each of the closes, find the nearest possible rounded line, add 1 to the counter for that line
    # initialising empty accumulator
    accumulator = np.zeros(len(rounded_lines),dtype=int)
    for close in dataframe["close"]:
        closest_line=min(rounded_lines,key=lambda x: abs(x-close))
        index=np.where(rounded_lines == closest_line)
        accumulator[index]=accumulator[index]+1
    accumulator_price_table=pd.DataFrame({'price':rounded_lines,'votes':accumulator})
    accumulator_price_table.sort_values(by=["votes"],ascending=False, inplace=True)

def get_ma(symbol,window):
    timestamp=client._get_earliest_valid_timestamp(symbol,'1d') #using daily for now, gets earliest timestamp
    kline=binance.fetchOHLCV(symbol,'1d')
    openings=list(map(lambda x: float(x[1]),kline))
    moving_averages=[]
    for i in range(window,len(openings)):
        averaging_list=openings[i-window:i]
        new_average=statistics.mean(averaging_list)
        moving_averages.append(new_average)
    return moving_averages

def get_support(symbol):
    stationary_points=get_stationary_points('4 hr',symbol,'2 weeks ago')
    get_horizontal_lines(stationary_points)
    
def get_macd(symbol): #takes in candlestick data returns latest 3 macd values
    endpoint = f"https://api.taapi.io/macdfix"
    macd=[]
    # n=len(data)
    for i in range(2,-1,-1):
        parameters = {
        'secret': taapi_key,
        'exchange': 'binance',
        'symbol': symbol,
        'interval': '1h',
        'backtrack': str(i),
        }
        # price_list=data[0:i]
        # parameters = {
        #     'secret': taapi_key,
        #     'candles': price_list,
        # } 
        response = requests.get(url = endpoint, params = parameters)
        result=response.json()
        print(result)
        time.sleep(60)
        macd.append(result['valueMACDHist'])
    print(macd)

# since_time=get_current_time(binance)-convert_to_milliseconds(2)
# candles=binance.fetchOHLCV('LINK/USDT','1h',since=since_time)
# print(candles)
get_macd()
# identify_trend('ETHUSDT')
# get_support('XRPUSDT')
