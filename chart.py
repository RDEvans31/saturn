import asyncio
from binance.client import Client
from binance.enums import *
import user
# import asyncio
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
    data=None
    print("Getting klines for", s, "in time period ",t)
    try:
        data = (t,client.get_historical_klines(s,Client.KLINE_INTERVAL_5MINUTE,t))
    except Exception as e:
        print(e)
    return data

def get_1hr_klines(s,t):
    data=None
    print("Getting klines for", s, "in time period ",t)
    try:
        data = (t,client.get_historical_klines(s,Client.KLINE_INTERVAL_1HOUR,t))
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
                print(symbol, ": Could not get", kline[0] ,"klines")
            if len(kline[1])>0:
                
                highs=list(map(lambda x:x[2],kline[1]))
                lows=list(map(lambda x:x[3],kline[1]))
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
    p=[]
    for i in range(0,len(data)-1):
        if data[i]>data[i+1] and data[i]>data[i-1]:
            p.append(data[i])
    return p

def get_troughs(data):
    t=[]
    for i in range(0,len(data)-1):
        if data[i]<data[i+1] and data[i]<data[i-1]:
            t.append(data[i])
    return t

def get_stationary_points(symbol,t):
    kline=get_1hr_klines(symbol,t)
    if kline!=None:
        closes=list(map(lambda x: x[4], kline[1]))
        peaks=get_peaks(closes)
        troughs=get_troughs(closes)

    return {'peaks': peaks, 'troughs': troughs}
    
