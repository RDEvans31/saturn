from matplotlib.pyplot import get
import numpy as np
import pandas as pd
from datetime import date
import ccxt
from pandas.core.base import DataError
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

binance = ccxt.binance({
    'apiKey': 'HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK',
    'secret': '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4',
    'timeout': 30000,
    'enableRateLimit': True,
})

phemex = ccxt.phemex({
    'secret' : 'GgWgKUdSCiSirVXS9fmXd4_th-SeXFjMr9g_HmJBgFU2MjQ0ZDMzMy04NmVkLTQ3ZmMtOGNlMC02MDZmZTJjMzEzYWM',
    'enableRateLimit': True,
})
ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

def update_csv(symbol,):
    pass

#GETTING INFORMATION
def find_start(candles,api=True):
    start_found=False
    if api:
        timestamps=list(map(lambda x:x[0]/1000,candles))
    else:
        timestamps=list(map(lambda x:x[0],candles))
    index=0
    while not(start_found):
        day=date.fromtimestamp(timestamps[index]).weekday()
        if day==0:
            start_found=True
        else:
            index=index+1
    return index

def convert_to_milliseconds(h): #enter time in hours
    return h*3600*1000

# returns true if there are no more open orders for 
def no_symbol_open_orders(symbol):
    orders=list(filter(lambda x: x['symbol']==symbol, open_orders))
    if len(orders)==0:
        return True
    else:
        return False

def get_current_price(symbol):
    price_data=get_price_data(interval='1m',symbol=symbol)
    return price_data.iloc[-1]['close']

# takes in the kline data and returns dataframe of timestamps and closing prices, could be adjusted for more price data
def get_price_data(interval, exchange=ftx, since=None, symbol=None, data=pd.DataFrame([])): 
    weekly=False
    weekly_candles=[]
    if interval=='1w':
        interval='1d'
        weekly=True

    if not(data.empty):
        candles=[]
        for i in range(len(data)):
            candle=data.iloc[i]
            candles.append((candle['unix'],candle['open'], candle['high'],candle['low'], candle['close']))

    elif symbol !=None:
        try:
                candles=exchange.fetchOHLCV(symbol,interval,since=since)
        except: 
            print('error fetching price')
            quit()
    candles=candles[find_start(candles,data.empty):]
    if weekly:
        # candles=candles[find_start(candles):]
        no_full_weeks=len(candles)//7
        for i in range(0,no_full_weeks):
            start=i*7
            end=start+7 #this is the index after the last day of the week
            week=candles[start:end]
            timestamp = week[6][0]
            open = week[0][1]
            high = max(list(map(lambda x: x[2], week)))
            low = min(list (map(lambda x: x[3], week)))
            close = week[6][4]
            weekly_candles.append((timestamp,open,high,low,close))
        week_in_progress=candles[no_full_weeks*7:len(candles)]
        timestamp = week_in_progress[0][0]
        open = week_in_progress[0][1]
        high = max(list(map(lambda x: x[2], week_in_progress)))
        low = min(list (map(lambda x: x[3], week_in_progress)))
        close = week_in_progress[-1][4]
        weekly_candles.append((timestamp,open,high,low,close))

        candles=weekly_candles
    if data.empty:
        timestamps=list(map(lambda x: x[0]/1000, candles))
    else:
        timestamps=list(map(lambda x: x[0], candles))
    open_price=np.array(list(map(lambda x: x[1], candles)),dtype=float)
    highest=np.array(list(map(lambda x: x[2], candles)),dtype=float)
    lowest=np.array(list(map(lambda x: x[3], candles)),dtype=float)
    closes=np.array(list(map(lambda x: x[4], candles)),dtype=float)

    return pd.DataFrame({'unix':timestamps,'open':open_price,'high':highest,'low':lowest,'close':closes}).sort_values(by=['unix'], ignore_index=True)

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://countries.trevorblades.com/")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
    query MyQuery {
        BTCUSD_1d {
            close
        }
    }
"""
)

# Execute the query on the transport
result = client.execute(query)
print(result)