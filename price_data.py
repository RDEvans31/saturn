from calendar import calendar
import numpy as np
import pandas as pd
from datetime import date
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

phemex = ccxt.phemex({
    'secret' : 'GgWgKUdSCiSirVXS9fmXd4_th-SeXFjMr9g_HmJBgFU2MjQ0ZDMzMy04NmVkLTQ3ZmMtOGNlMC02MDZmZTJjMzEzYWM',
    'enableRateLimit': True,
})
ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

#GETTING INFORMATION
def find_start(candles):
    start_found=False
    timestamps=list(map(lambda x:x[0],candles))
    index=0
    while not(start_found):
        day=date.fromtimestamp(timestamps[index]/1000).weekday()
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
        df=df.append(candle,ignore_index=True)

    return df.sort_values(by=['unix'], ignore_index=True)

    return result
    
# takes in the kline data and returns dataframe of timestamps and closing prices, could be adjusted for more price data
def get_price_data(timeframe, exchange=ftx, since=None, symbol=None, data=pd.DataFrame([])): 
    
    weekly=False
    weekly_candles=[]
    if timeframe=='1w':
        timeframe='1d'
        weekly=True

    if not(data.empty):
        candles=[]
        for i in range(len(data)):
            candle=data.iloc[i]
            candles.append((candle['unix'],candle['open'], candle['high'],candle['low'], candle['close']))

    elif symbol !=None:
        candles_retrieved=False
        while not(candles_retrieved):
            try:
                candles=exchange.fetchOHLCV(symbol,timeframe,since=since)
                candles_retrieved=True
            except: 
                print('error fetching price')
            if not(candles_retrieved):
                print('retrying')
            
    if weekly:
        start=find_start(candles)
        candles=candles[start:]
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
    timestamps=list(map(lambda x: x[0], candles))
    open_price=np.array(list(map(lambda x: x[1], candles)),dtype=float)
    highest=np.array(list(map(lambda x: x[2], candles)),dtype=float)
    lowest=np.array(list(map(lambda x: x[3], candles)),dtype=float)
    closes=np.array(list(map(lambda x: x[4], candles)),dtype=float)

    df=pd.DataFrame({'unix':timestamps,'open':open_price,'high':highest,'low':lowest,'close':closes}).sort_values(by=['unix'], ignore_index=True)

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
                delete_ETHUSD_1d(where: { unix: {_eq: $unix} } ){
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
    
