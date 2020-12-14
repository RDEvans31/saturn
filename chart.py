import asyncio
from binance.client import Client
from binance.enums import *
import user
import numpy as np
import pandas as pd

client=user.client
open_orders=client.futures_get_open_orders()
time_periods=['1 hour ago', '2 hours ago', '3 hours ago','4 hours ago']


# returns true if there are no more open orders for 
def symbol_open_orders(symbol):
    orders=list(filter(lambda x: x['symbol']==symbol, open_orders))
    if len(orders)==0:
        return True
    else:
        return False

def get_5min_klines(s,t):
    data=[]
    print("Getting klines for", s, "in time period ",t)
    try:
        data = client.get_historical_klines(s,Client.KLINE_INTERVAL_5MINUTE,t)
    except Exception as e:
        print(e)
    return data

def get_1hr_klines(s,t):
    data=[]
    print("Getting klines for", s, "in time period ",t)
    try:
        data = client.get_historical_klines(s,Client.KLINE_INTERVAL_1HOUR,t)
    except Exception as e:
        print(e)
    return data

def get_4hr_klines(s,t):
    data=[]
    print("Getting klines for", s, "in time period ",t)
    try:
        data = client.get_historical_klines(s,Client.KLINE_INTERVAL_4HOUR,t)
    except Exception as e:
        print(e)
    return data

def get_day_klines(s,t):
    data=[]
    print("Getting klines for", s, "in time period ",t)
    try:
        data = client.get_historical_klines(s,Client.KLINE_INTERVAL_1DAY,t)
    except Exception as e:
        print(e)
    return data

def get_viable_trades_for_symbol(symbol):
    print('Checking:', symbol)
    if symbol_open_orders(symbol):
        trade_found=False
        i=len(time_periods)-1
        while not(trade_found) and i>=0:
            kline=(symbol,[])
            try:
                kline= get_5min_klines(symbol,time_periods[i])
            except:
                print(symbol, ": Could not get", time_periods[i] ,"klines")
            if len(kline[1])>0:
                
                highs=list(map(lambda x:x[2],kline))
                lows=list(map(lambda x:x[3],kline))
                top=float(max(highs))
                bottom=float(min(lows))
                if bottom>top*0.98 and bottom<top*0.995:
                    trade=(symbol,top,bottom,i)
                    trade_found=True 
                    #print('Trade found.')
                else:
                    i=i-1
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
        closes=get_closes(data)
        peaks=[]
        for i in range(1,len(data)-1):
            if closes[i]>closes[i+1] and closes[i]>closes[i-1]:
                peaks.append((data[i][0],closes[i]))
    
        return peaks
    else:
        return None

def get_troughs(data):
    if len(data)>0:
        closes=get_closes(data)
        troughs=[]
        
        for i in range(1,len(data)-1):
            if closes[i]<closes[i+1] and closes[i]<closes[i-1]:
                troughs.append((data[i][0],closes[i]))

        return troughs
    else:
        return None

def get_stationary_points(interval,symbol,t):
    kline=None
    peaks=None
    troughs=None
    if interval=='1 hr':
        kline=get_1hr_klines(symbol,t)
    elif interval=='4 hr':
        kline=get_4hr_klines(symbol,t)
    elif interval=='1 day':
        kline=get_day_klines(symbol,t)

    if kline!=None:
        
        peaks=get_peaks(kline)
        troughs=get_troughs(kline)

    return {'peaks': peaks,'troughs': troughs}
    
def identify_trend(symbol):
    closes=get_closes(get_1hr_klines(symbol,'1 day ago'))

    y=np.array(closes['closes'],dtype=float)
    x=np.array(closes['timestamps'],dtype=float)

    dataframe=pd.DataFrame({'time':x,'price':y})
    print(dataframe)
    m, c=np.polyfit(x,y,1)
    print(m,c)

    if m>1.2:
        return 'BULL'
    if m<0.8:
        return 'BEAR'

def get_closes(kline):
    timestamps=list(map(lambda x: x[0], kline))
    timestamp_hr=list(map(lambda x: (x-timestamps[0])/3600000, timestamps))
    closes=list(map(lambda x: x[4], kline))

    return {'timestamps':timestamp_hr,'closes':closes}

identify_trend('ETHUSDT')