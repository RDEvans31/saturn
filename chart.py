import ccxt
import statistics
import time
from pprint import pprint
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from scipy.stats import norm
import math
import price_data as price
import sys 

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

def get_ema(data,window, close=False):
    timestamps=data['unix'][window:]
    if close:
        ema=data.ewm(span=window,min_periods=window+1, adjust=False).mean()['close'].dropna()
    else:
        ema=data.ewm(span=window,min_periods=window+1, adjust=False).mean()['open'].dropna()
    return pd.DataFrame({'unix': timestamps,'value':ema})

def get_dema(data,window,close=False):
    ema=get_ema(data,window)
    ema=ema.rename(columns={'value':'open'})
    smoothed_ema=get_ema(ema,window)
    #making both vectors the same length
    start=np.min(smoothed_ema.index.values)
    ema=ema.loc[start:]
    timestamps=ema['unix'].values
    ema=ema['open'].values
    smoothed_ema=smoothed_ema['value'].values
    dema=2*ema-smoothed_ema
    return pd.DataFrame({'unix': timestamps,'value':dema})

def identify_trend(daily, hourly,daily_ema_period,hourly_ema_period): #using moving average channel and gradient of large timeframe moving average
    long_ema=get_ema(daily,daily_ema_period,False)
    channel=ma_channel(hourly,hourly_ema_period)

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
def risk_indicator(fast,slow):
    min_timestamp=max(fast['unix'].min(),slow['unix'].min())

    trimmed_fast=fast.loc[fast['unix']>=min_timestamp]
    slow=slow.loc[slow['unix']>=min_timestamp]
    if len(trimmed_fast)>len(slow): 
        #different values, ie using a daily for fast and weekly for slow
        if (slow['unix'].max()<trimmed_fast['unix'].max()):
            print('true')
            #add another value to the slow moving avarage to facilitate interpolation
            slow=slow.append({'unix': trimmed_fast['unix'].max(), 'value':slow.iloc[-1]['value']},ignore_index=True)
        f=interp1d(slow['unix'],slow['value'])
        slow_interpolated=f(trimmed_fast['unix'])
        slow=pd.DataFrame({'unix':trimmed_fast['unix'],'value':slow_interpolated})

    if ('close' in fast.columns.values.tolist()):
        #using price
        risk_metric=np.divide(trimmed_fast['close'],slow['value'])
    else:
        #using moving average
        risk_metric=np.divide(trimmed_fast['value'],slow['value'])

    mean=np.mean(risk_metric)
    sigma=np.std(risk_metric)
    normalised=(risk_metric-mean)/sigma
    risk=norm.cdf(normalised)
    return pd.DataFrame({'unix':trimmed_fast['unix'],'value':risk})

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

def get_rsi(candles, periods=14):
    close_delta = candles['close'].diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    
    # Use exponential moving average
    ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
    ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi

def get_atr(candles,periods=14):
    tr=[]
    index=[]
    for i in range(len(candles)):
        candle=candles.iloc[i]
        high=candle['high']
        low=candle['low']
        close=candle['close']
        true_range=max([high-low,abs(high-close),abs(close-low)])
        tr.append(true_range)
        index.append(candle['unix'])
    tr=pd.Series(tr, index=index)
    atr = tr.rolling(window=periods).mean()

    return atr

def get_bb(data,period,multiple): #based on opening prices
    timestamps=data['unix'].iloc[period-1:]
    ma=data.rolling(period)['open'].mean().dropna()
    std=data.rolling(period)['open'].std().dropna()
    upper_bb=ma+multiple*std
    lower_bb=ma-multiple*std

    return pd.DataFrame({'unix':timestamps, 'ma': ma, 'upper':upper_bb,'lower':lower_bb})

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