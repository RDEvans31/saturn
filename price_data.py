from calendar import calendar
from math import remainder
import numpy as np
import pandas as pd
from datetime import date, datetime
import ccxt
from pandas.core.base import DataError
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

binance = ccxt.binance({
    'apiKey': 'HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK',
    'secret': '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4',
    'timeout': 30000,
    'enableRateLimit': True,
})

cex= ccxt.cex({
    'uid' : 'up109520414',
    'apiKey': '1X2uEcPlvBCe4CcMtzWKguG1SDI',
    'secret': '8JY4fDg6hRz0DTolZHz77XPdC1o',
    'enableRateLimit': True,
    })

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

#GETTING INFORMATION
def find_start(candles, timeframe='weekly'):
    start_found=False
    timestamps=list(map(lambda x:x[0],candles))
    index=0
    while not(start_found):
        if timeframe=='weekly':
            day=date.fromtimestamp(timestamps[index]/1000).weekday()
            if day==0:
                start_found=True
            else:   
                index=index+1
        elif timeframe=='4h':
            remainder=datetime.fromtimestamp(timestamps[index]/1000).hour %  4
            if remainder == 0:
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
    price_data=get_price_data(timeframe='1m',symbol=symbol)
    return price_data.iloc[-1]['close']

def get_stored_data(symbol,timeframe):
    # Provide a GraphQL query
    split_symbol=symbol.split('/')
    base_currency=split_symbol[0]
    quote_currency=split_symbol[1]
    table=base_currency+quote_currency+'_'+timeframe
    if table=='BTCUSD_1d':
        query = gql(
            """
            query MyQuery {
                BTCUSD_1d {
                    unix
                    close
                    high
                    low
                    open
                }
            }
        """
        )
    elif table=='ETHUSD_1d':
        query = gql(
            """
            query MyQuery {
                ETHUSD_1d {
                    unix
                    close
                    high
                    low
                    open
                }
            }
        """
        )
    elif table=='ETHBTC_1d':
        query = gql(
            """
            query MyQuery {
                ETHBTC_1d {
                    unix
                    close
                    high
                    low
                    open
                }
            }
        """
        )
    else:
        return 'no such table'

    # Execute the query on the transport
    result = client.execute(query)
    candles=result[table]
    df=pd.DataFrame({},columns=['unix','close','high','low','open'])
    for candle in candles:
        df=pd.concat([df,pd.DataFrame(candle,index=[0]).astype('float64')], ignore_index=True)
        # df=df.append(candle,ignore_index=True)

    return df.sort_values(by=['unix'], ignore_index=True)
    
# takes in the kline data and returns dataframe of timestamps and closing prices, could be adjusted for more price data
def get_price_data(timeframe, exchange_str='ftx', since=None, symbol=None, data=pd.DataFrame([])): 

    timeframes = {
        '1w': '1d', 
        '4h': '1h',
        '1d': '1d',
        '1h': '1h',
        '1m': '1m',
        }

    timeframe_encoded = timeframes[timeframe]

    exchange=ftx
    if exchange_str=='binance':
        exchange=binance
    elif exchange_str=='cex':
        exchange=cex

    period_candles=[]

    if not(data.empty):
        candles=[]
        for i in range(len(data)):
            candle=data.iloc[i]
            candles.append((candle['unix'],candle['open'], candle['high'],candle['low'], candle['close']))

    elif symbol !=None:
        candles_retrieved=False
        while not(candles_retrieved):
            try:
                candles=exchange.fetchOHLCV(symbol,timeframe_encoded,since=since)
                candles_retrieved=True
            except: 
                print('error fetching price')
            if not(candles_retrieved):
                exchange = cex
                print('retrying')

    if timeframe == '4h':
        print('runnning')
        start=find_start(candles, '4h')
        candles=candles[start:]
        no_periods=len(candles)//4
        for i in range(0,no_periods):
            start=i*4
            end=start+4 #this is the index after the last day of the week
            period=candles[start:end]
            timestamp = period[0][0]
            open = period[0][1]
            high = max(list(map(lambda x: x[2], period)))
            low = min(list (map(lambda x: x[3], period)))
            close = period[-1][4]
            period_candles.append((timestamp,open,high,low,close))
        candle_in_progress=candles[no_periods*4:len(candles)]
        if len(candle_in_progress)>0:
            timestamp = candle_in_progress [0][0]
            open = candle_in_progress [0][1]
            high = max(list(map(lambda x: x[2], candle_in_progress )))
            low = min(list (map(lambda x: x[3], candle_in_progress )))
            close = candle_in_progress [-1][4]
            period_candles.append((timestamp,open,high,low,close))
        
        candles = period_candles
            
    elif timeframe == '1w':
        start=find_start(candles)
        candles=candles[start:]
        no_full_weeks=len(candles)//7
        for i in range(0,no_full_weeks):
            start=i*7
            end=start+7 #this is the index after the last day of the week
            week=candles[start:end]
            timestamp = week[0][0]
            open = week[0][1]
            high = max(list(map(lambda x: x[2], week)))
            low = min(list (map(lambda x: x[3], week)))
            close = week[-1][4]
            period_candles.append((timestamp,open,high,low,close))
        week_in_progress=candles[no_full_weeks*7:len(candles)]
        if len(week_in_progress)>0:
            timestamp = week_in_progress[0][0]
            open = week_in_progress[0][1]
            high = max(list(map(lambda x: x[2], week_in_progress)))
            low = min(list (map(lambda x: x[3], week_in_progress)))
            close = week_in_progress[-1][4]
            period_candles.append((timestamp,open,high,low,close))

        candles=period_candles
    timestamps=list(map(lambda x: x[0], candles))
    open_price=np.array(list(map(lambda x: x[1], candles)),dtype=float)
    highest=np.array(list(map(lambda x: x[2], candles)),dtype=float)
    lowest=np.array(list(map(lambda x: x[3], candles)),dtype=float)
    closes=np.array(list(map(lambda x: x[4], candles)),dtype=float)

    df=pd.DataFrame({'unix':timestamps,'close':closes,'high':highest,'low':lowest,'open':open_price}).sort_values(by=['unix'], ignore_index=True)

    return df

def get_missing_data(symbol,timeframe):
    old_data=get_stored_data(symbol, timeframe)
    new_data=get_price_data(timeframe,symbol=symbol)
    max_timestamp=old_data['unix'].max()
    missing_data=new_data.loc[new_data['unix']>=max_timestamp]
    return missing_data

def update_database(symbol,timeframe):

    missing_data=get_missing_data(symbol, timeframe)

    split_symbol=symbol.split('/')
    base_currency=split_symbol[0]
    quote_currency=split_symbol[1]
    table=base_currency+quote_currency+'_'+timeframe
    print(table)
    if table=='BTCUSD_1d':
        query = gql(
            """
              mutation AddCandle ( $unix: numeric, $close: numeric, $high: numeric, $low: numeric, $open: numeric ){
                insert_BTCUSD_1d(objects: { unix: $unix, close: $close, high: $high, low: $low, open: $open }){
                    affected_rows
                }
            }
        """
        )

        delete= gql(
            """
              mutation DeleteCandle ( $unix: numeric ){
                delete_BTCUSD_1d(where: { unix: {_eq: $unix} } ){
                    affected_rows
                }
            }
        """
        )
        params={"unix": missing_data.iloc[0]['unix']}
        print(client.execute(delete,variable_values=params))
    elif table=='ETHUSD_1d':
        #
        query = gql(
            """
              mutation AddCandle ( $unix: numeric, $close: numeric, $high: numeric, $low: numeric, $open: numeric ){
                insert_ETHUSD_1d(objects: { unix: $unix, close: $close, high: $high, low: $low, open: $open }){
                    affected_rows
                }
            }
        """
        )

        delete= gql(
            """
              mutation DeleteCandle ( $unix: numeric ){
                delete_ETHUSD_1d(where: { unix: {_eq: $unix}}){
                    affected_rows
                }
            }
        """
        )
        params={"unix": missing_data.iloc[0]['unix']}
        print(client.execute(delete,variable_values=params))

    elif table=='ETHBTC_1d':
        query = gql(
            """
              mutation AddCandle ( $unix: numeric, $close: numeric, $high: numeric, $low: numeric, $open: numeric ){
                insert_ETHBTC_1d(objects: { unix: $unix, close: $close, high: $high, low: $low, open: $open }){
                    affected_rows
                }
            }
        """
        )

        delete= gql(
            """
              mutation DeleteCandle ( $unix: numeric ){
                delete_ETHBTC_1d(where: { unix: {_eq: $unix} } ){
                    affected_rows
                }
            }
        """
        )
        params={"unix": missing_data.iloc[0]['unix']}
        print(client.execute(delete,variable_values=params))
    else:
        return 'no such table'
    #the first of the missing data is the complete candle of the last value (which is incomplete at the time of fetching)
    # we need to delete it
    print('updating ', len(missing_data), ' rows')
    for i in range(0,len(missing_data)):
        candle=missing_data.iloc[i]
        params={"unix": candle['unix'], "close": candle['close'], "high": candle['high'], "low": candle['low'], "open": candle["open"]}
        client.execute(query, variable_values=params)

def heikin_ashi(previous_open, previous_close, candle):
    # print(candle)
    price_values = candle[["open","high","low","close"]]
    close = np.mean(price_values)
    open_price = 0.5*(previous_open+previous_close)
    high=max([max(price_values), open_price,close])
    low = min([min(price_values), open_price,close])
    
    return candle["unix"], open_price, high, close, low

def convert_data_to_heikin_ashi(data):
    timestamps, opens, closes, highs, lows  = [0], [0],[0],[0],[0]
    #initialise values
    for i in range(1,len(data)):
        timestamp, open_price, high, close, low = heikin_ashi(opens[-1], closes[-1],data.iloc[i])
        timestamps.append(timestamp)
        opens.append(open_price)
        highs.append(high)
        lows.append(low)
        closes.append(close)

    candles = pd.DataFrame({'unix':timestamps,'ha_Open':opens,'ha_High':highs,'ha_Low':lows,'ha_Close':closes}).sort_values(by=['unix'], ignore_index=True)
    timestamp_df=candles['unix'].shift(periods=-1)
    candles["unix"] = timestamp_df
    candles["Date"] = pd.to_datetime(candles["unix"], unit="ms")
    candles["Green"] = candles["ha_Close"]>candles["ha_Open"]
    candles.drop([0,1,len(candles)-1], inplace=True)
    candles.set_index("Date", inplace=True)
    candles.drop("unix", axis=1, inplace=True)
    return candles

