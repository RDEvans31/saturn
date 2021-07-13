import ccxt
import statistics
import time
from pprint import pprint
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import math
import price_data as price
import sys 


# def get_viable_trades_for_symbol(symbol):
#     print('Checking:', symbol)
#     trade_options=[]
#     output=[]
#     if no_symbol_open_orders(symbol):
#         trade_found=False
#         try:
#             macd=get_macd(symbol,'1h')
#             all_rsi=get_all_rsi(symbol)
#             ma_trend=get_ma_trend(symbol)
#         except:
#             print('Could not get either macd or rsi or sma')
#             return

#         trade_options=trade_detector(all_rsi,macd,ma_trend)
        
#         if trade_options != []:
#             print('Trade options found')
#             for trade_option in trade_options:
#                 risk_multiplier=trade_option[1]
#                 sl=get_sl(symbol,trade_option[0])
#                 if sl==None:
#                     print('No sl found, skipping')
#                     continue
#                 price=get_current_price(symbol)
#                 tp_array=get_tp(trade_option[0],symbol,price)
#                 risk_reward=get_risk_reward(sl,tp_array,price)
#                 trade=(trade_option[0],symbol,risk_multiplier,sl,tp_array,risk_reward)
#                 output.append(trade)
#             return output
#         else:
#             #print('Could not find trade for ', symbol)
#             return
#     else:
#         #print('There are open orders for ', symbol)
#         return

# #uses 15m candles from an hour ago to get most recent highs or lows
# # def get_nearest_sl(trade_side,symbol,current_price):

# #     candles=price.get_price_data(symbol,'15m',since=binance.fetch_time()-price.convert_to_milliseconds(1))

# #     if trade_side:
# #         index=candles['low'].idxmin()
# #         extreme=candles.loc[index]['low']
# #         close=candles.loc[index]['close']
# #     else:
# #         index=candles['high'].idxmax()
# #         extreme=candles.loc[index]['high']
# #         close=candles.loc[index]['close']

# #     sl=extreme
    
# #     if (trade_side and sl<current_price) or (not(trade_side) and sl>current_price):
# #         return sl
# #     else:
# #         print('No sl found')
# #         return None

# def viable_sl(trade_side,stationary_points,current_price):
#     index=None
#     if trade_side: #trade is a long 
#         if len(stationary_points.index) > 0:
#             index=stationary_points['close'].idxmin()

#     else: #trade is short
#         if len(stationary_points.index) > 0:
#             index=stationary_points['close'].idxmax()
        

#     if index != None:
#         extreme=stationary_points.loc[index]['extreme']
#         close=stationary_points.loc[index]['close']
#         if (abs(close-extreme)/close) > 0.05:
#             sl=statistics.mean([close,extreme])
#         else:
#             sl=extreme

#         if (trade_side and sl<current_price) or (not(trade_side) and sl>current_price):
#             return sl
#         else: 
#             return None
#     else:
#         return None

# def get_sl(symbol,trade_side,interval='1h'): 
#     since_time=binance.fetch_time()-price.convert_to_milliseconds(48)#fetches unix for 48 hrs before
#     candles_48=price.get_price_data(symbol,interval,since=since_time)
#     #gets relevant stationary points
#     if trade_side:
#         stationary_points_48=get_minima(candles_48)
#     else:
#         stationary_points_48=get_maxima(candles_48)
    
#     stationary_points_36=stationary_points_48.loc[stationary_points_48['unix']>=11] 
#     stationary_points_24=stationary_points_48.loc[stationary_points_48['unix']>=23]
#     stationary_points_18=stationary_points_48.loc[stationary_points_48['unix']>=29]
#     stationary_points_12=stationary_points_48.loc[stationary_points_48['unix']>=35]
#     stationary_points=[stationary_points_12,stationary_points_18,stationary_points_24,stationary_points_36,stationary_points_48]

#     sl_found=False
    
#     index=0
#     current_price=get_current_price(symbol)

#     while not(sl_found) and index<len(stationary_points):
#         points=stationary_points[index]
#         index += 1
#         possible_sl=viable_sl(trade_side,points, current_price)
#         if possible_sl != None:
#             sl=possible_sl
#             sl_found=True
    
#     if sl_found:
#         return sl
#     else:
#         return None

# def get_fibs(symbol,interval='5m'):

#     fib_values=[0,0.236,0.382,0.5,0.618,0.786,1]
#     since_time=binance.fetch_time()-price.convert_to_milliseconds(24)#fetches unix for 12 hrs before
#     candles=binance.fetchOHLCV(symbol,interval,since=since_time)
#     highs=list(map(lambda x: x[2],candles))
#     lows=list(map(lambda x: x[3],candles))
#     high=float(max(highs))
#     low=float(min(lows))
#     fib_levels=list(map(lambda x: low+(high-low)*x,fib_values))

#     return fib_levels

# def get_tp(buy,symbol,current_price):
#     #get current price
#     fibs=get_fibs(symbol)
#     tp=[]
#     price=current_price
#     # print(binance.decimal_to_precision(price))
#     if buy:
#         tp=list(filter(lambda x: x>1.01*price, fibs))
#     else:
#         tp=list(filter(lambda x: x<0.99*price, fibs))

#     return fibs

# def get_risk_reward(sl,tp_array,entry):
#     min_reward=min([tp_array[-1],tp_array[0]])
#     risk=abs(sl-entry)
#     return risk/min_reward

#trend analysis

def get_gradient(ma):
    
    return pd.Series(
        index=ma['unix'].values,
        data=np.gradient(ma['value'])
    )

def ma_channel(data, window):
    timestamps=data['unix']
    sma=data.rolling(window).mean()
    sma['unix']=timestamps
    sma.dropna(inplace=True)    

    return pd.DataFrame({'unix':sma['unix'],'high':sma['high'], 'low':sma['low'], 'open':sma['open']})

def get_sma(data,window, close=True):
     #using daily for now
    timestamps=data['unix'][window-1:]
    if close:
        sma=data.rolling(window).mean()['close'].dropna()
    else:
        sma=data.rolling(window).mean()['open'].dropna()
    return pd.DataFrame({'unix': timestamps,'value':sma})

    # return pd.DataFrame({'unix': list(map(lambda x: x[0], sma)),'value':list(map(lambda x: x[1], sma))})

def get_ema(data,window, close=True):
    timestamps=data['unix'][window:]
    if close:
        ema=data.ewm(span=window,min_periods=window+1, adjust=False).mean()['close'].dropna()
    else:
        ema=data.ewm(span=window,min_periods=window+1, adjust=False).mean()['open'].dropna()
    return pd.DataFrame({'unix': timestamps,'value':ema})

def identify_trend(daily, hourly): #using moving average channel and gradient of large timeframe moving average
    long_ema=get_ema(daily,25,False)
    channel=ma_channel(hourly,20)

    gradient = get_gradient(long_ema)
    upper_bound=channel.iloc[-1]['high']
    lower_bound=channel.iloc[-1]['low']
    day=max(gradient.index)
    five_opens=hourly.tail(n=5)['open'].values
    uptrend=gradient.loc[day]>0
    current=five_opens[-1]

    if all(opens>upper_bound for opens in five_opens) and uptrend.all():
        return 'uptrend'
    elif all(opens<lower_bound for opens in five_opens) and not(uptrend.all()):
        return 'downtrend'
    else:
        return 'neutral'

#data analysis
def get_maxima(data, range_param=3):
    n=len(data.index)
    if n>0:
        peaks=[]
        for i in range(3,n):
            current_series=data.iloc[i]
            domain_range=min([n-1-i,range_param])
            subset=[]
            if domain_range==range_param:
                subset=data.iloc[i-range_param:i+range_param+1]
            else:
                subset=data.iloc[i-range_param:i+domain_range+1]

            if current_series['high']==subset['high'].max():
                peaks.append([current_series['unix'],current_series['close'],current_series['high']])
     
        peaks_df=pd.DataFrame(data=peaks,columns=['unix','close','extreme'])
        return peaks_df.sort_values(by='unix',ascending=False)
    else:
        return None

def get_minima(data, range_param=3):
    n=len(data.index) #last index
    if n>0:
        troughs=[]
        for i in range(3,n):
            current_series=data.iloc[i]
            domain_range=min([n-1-i,3])
            domain_range=min([n-1-i,range_param])
            subset=[]
            if domain_range==range_param:
                subset=data.iloc[i-range_param:i+range_param+1]
            else:
                subset=data.iloc[i-range_param:i+domain_range+1]

            if current_series['low']==subset['low'].min():
                troughs.append([current_series['unix'],current_series['close'],current_series['low']])

        troughs_df=pd.DataFrame(data=troughs,columns=['unix','close','extreme'])
        return troughs_df.sort_values(by='unix',ascending=False)
    else:
        return None

def get_generic_maxima(dataframe, metric_column, range_param=1): #assumes dataframe[metric column] is unique
    metric=str(metric_column)
    n=len(dataframe.index)
    if n>0:
        peak_indices = find_peaks(np.array(dataframe[metric]))[0].tolist()
        peaks_df = dataframe.iloc[peak_indices]
        # peaks=[]
        # for i in range(3,n):
        #     current_series=dataframe.iloc[i]
        #     domain_range=min([n-1-i,range_param])
        #     subset=[]
        #     if domain_range==range_param:
        #         subset=dataframe.iloc[i-range_param:i+range_param+1]
        #     else:
        #         subset=dataframe.iloc[i-range_param:i+domain_range+1]

        #     if current_series[]==subset['high'].max():
        #         peaks.append(current_series)
     
        # peaks_df=pd.DataFrame(data=peaks,columns=list(dataframe.columns))
        return peaks_df#.sort_values(ascending=False)
    else:
        return None

def get_support_resistance(price_data):
    maxima=get_maxima(price_data,1)
    minima=get_minima(price_data,1)
    raw_data=[]+price_data['high'].values.tolist()+price_data['close'].values.tolist()+price_data['low'].values.tolist()
    maxima_minima=[]+maxima['extreme'].values.tolist()+minima['extreme'].values.tolist()
    support_resistance_lines=get_horizontal_lines(raw_data, maxima_minima)
    cleaned_result=clean_results(support_resistance_lines, price_data)
    return cleaned_result

def get_deviations(line, price_data):
    def deviated(candle, line):
        open_price=candle['open']
        close_price=candle['close']
        if (open_price>line and close_price<line) or (open_price<line and close_price>line):
            return True
        else:
            return False
    deviated_candles=price_data.apply(deviated, args=(line,), axis=1)
    deviations=len(price_data[deviated_candles].index)
    return deviations

def clean_results(raw_support_resistance, price_data):
    #whether or not a line is significant is dependent on 3 parameters (v, d, t_s)
    # v- votes for that line (number of datapoints confluent) *porportional
    # d - number of deviations (price opens on one side, closes on the other) *inverse
    # t_s - time siginifance (depends on dsitribution of votes with time)
    current_price=price_data['close'].iloc[0]
    result=raw_support_resistance[(raw_support_resistance['price'] < 1.5*current_price) & (raw_support_resistance['price'] > 0.5*current_price)]
    
    deviations_series=result['price'].apply(get_deviations, args=(price_data,))
    result=result.assign(deviations=deviations_series)
    print('pretty_printing')
    pprint(result)
    result=get_generic_maxima(raw_support_resistance,'datapoints')
    pass

def get_horizontal_lines(raw_data,maxima_minima): #raw list containing all maxima and minima in one dimension
    # rounding closing prices
    sup=max(raw_data)
    inf=min(raw_data)
    sig_level=int(-(math.floor(math.log(inf,10))-2))
    round_func=np.vectorize(lambda x: round(x, sig_level))
    delta=sup-inf
    possible_lines=maxima_minima#np.linspace(inf,sup,num=int(round(15*math.exp(delta/sup),-1)))
    rounded_lines=np.unique(round_func(possible_lines))
    #for each of the closes, find the nearest possible rounded line, add 1 to the counter for that line
    # initialising empty accumulator
    accumulator = np.zeros(len(rounded_lines),dtype=int)
    for datapoint in raw_data:
        closest_line=min(rounded_lines,key=lambda x: abs(x-datapoint))
        if abs(closest_line-datapoint) < (sup-inf)/100:
            index=np.where(rounded_lines == closest_line)
            if datapoint == max(raw_data) or datapoint == min(raw_data):
                accumulator[index]=accumulator[index]+10
            else:
                accumulator[index]=accumulator[index]+1
            
    accumulator_price_table=pd.DataFrame({'price':rounded_lines,'datapoints':accumulator})
    accumulator_price_table.sort_values(by=['price'],ascending=False, inplace=True)
    significant_datapoints = accumulator_price_table['datapoints']>1
    significant_lines=accumulator_price_table[significant_datapoints]
    print('raw sig lines', significant_lines)
    return significant_lines

def get_ABC_fib_extension(price_data,uptrend, time_interval='1d'):
    fib_values=[0,0.236,0.382,0.5,0.618,0.786,1,1.618]
    get_ABC_fib_extension=[]
    if time_interval=='1h':
        range_param=12
    elif time_interval=='4h':
        range_param=3
    else:
        range_param=2
    highs=get_maxima(price_data,range_param=range_param)
    # highs.sort_values(by=['unix','extreme'], inplace=True)
    # print(highs)

    lows=get_minima(price_data,range_param=range_param)
    # lows.sort_values(by=['unix','unix'], inplace=True)
    # print(lows)

    A_found=False
    B_found=False
    C_found=False
    
    if uptrend:
        #looks for first peak, then checks either side
        B=highs.iloc[0]['extreme']
        B_unix=highs.iloc[0]['unix']
        before_B=lows['unix']<B_unix
        after_B=lows['unix']>B_unix
        if len(lows[after_B].index)==0:
            return
        C=lows[after_B]['extreme'].min()

        A=lows[before_B].iloc[0]['extreme']
        fib_extension=list(map(lambda x: x*(B-A)+C, fib_values))      

    else:
        B=lows.iloc[0]['extreme']
        B_unix=lows.iloc[0]['unix']
        before_B=highs['unix']<B_unix
        after_B=highs['unix']>B_unix
        if len(highs[after_B].index)==0:
            return
        C=highs[after_B]['extreme'].max()

        A=highs[before_B].iloc[0]['extreme']


        fib_extension=list(map(lambda x: C-x*(A-B), fib_values)) 

    print(A,B,C)
    return fib_extension

def get_swing_trade(symbol):
    trend=identify_trend(symbol,'1d')
    candles=price.get_price_data(binance,symbol,'1d')
    fib=get_ABC_fib_extension(candles,trend>2)
    return fib

# price_data=price.get_price_data(symbol='BTC/USDT', interval='4h')
# get_support_resistance(price_data)