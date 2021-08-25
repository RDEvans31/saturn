import ccxt
from scipy.stats import norm
import price_data as price
import chart
import time
import schedule
import numpy as np
import pandas as pd
import datetime as dt 
from ftx_client import FtxClient
from scheduler import Scheduler


ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

ftx.headers = {'FTX-SUBACCOUNT':'Minute_MeanReversion'}

main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
ShortTerm=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Minute_MeanReversion')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')

def get_free_balance():
    return float(next(filter(lambda x:x['coin']=='USD', ShortTerm.get_balances()))['free'])

def get_total_balance():
  return float(next(filter(lambda x:x['coin']=='USD', ShortTerm.get_balances()))['total'])

def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)

def update_model(state,price_data,channel):
    print('Updating model') #this will need to be routinely called to adjust for recent volatility
    global long_tp_mean
    global long_tp_std
    global short_tp_mean
    global short_tp_std

    diff=None
    if state=='neutral':
        high_diff=chart.get_differences(channel['unix'],channel['high'])
        high_diff=high_diff.loc[high_diff>0].abs()
        low_diff=chart.get_differences(channel['unix'],channel['low'])
        low_diff=low_diff.loc[low_diff<0].abs()
        long_times=high_diff.index
        short_times=low_diff.index
        long_opens=[]
        short_opens=[]
        for i in range(len(price_data['unix'])):
            if price_data['unix'].iloc[i] in long_times:
                current_open=price_data['open'].iloc[i]
                long_opens.append(current_open)
        for i in range(len(price_data['unix'])):
            if price_data['unix'].iloc[i] in short_times:
                current_open=price_data['open'].iloc[i]
                short_opens.append(current_open)

        long_opens=np.array(long_opens)
        short_opens=np.array(short_opens)
        difference_metric_long=high_diff/long_opens
        difference_metric_short=low_diff/short_opens


        long_tp_mean=difference_metric_long.mean()
        long_tp_std=difference_metric_long.std()

        short_tp_mean=difference_metric_short.mean()
        short_tp_std=difference_metric_short.std()
        return

    if state=='long':
        diff=chart.get_differences(channel['unix'],channel['high'])
        diff=diff.loc[diff>0].abs()
        
    elif state=='short':
        diff=chart.get_differences(channel['unix'],channel['low'])
        diff=diff.loc[diff<0].abs()

    times=diff.index
    corresponding_opens=[]
    for i in range(len(price_data['unix'])):
        if price_data['unix'].iloc[i] in times:
            current_open=price_data['open'].iloc[i]
            corresponding_opens.append(current_open)
    corresponding_opens=np.array(corresponding_opens)
    difference_metric_series=diff/corresponding_opens
    mean=difference_metric_series.mean()
    std=difference_metric_series.std()

    if state=='long':
        long_tp_mean=mean
        long_tp_std=std
    elif state=='short':
        short_tp_mean=mean
        short_tp_std=std

def tp_indicator(state,previous,current_price):
    global long_tp_mean
    global long_tp_std
    global short_tp_mean
    global short_tp_std
    # print('Means and stds: ', long_tp_mean,long_tp_std,short_tp_mean,short_tp_std)
    diff=abs(current_price-previous)/current_price
    print('state: %s, previous %s: current: %s' % (state,previous,current_price))
    normalised=0
    mean=None
    std=None
    #indicator=False
    if state=='long' and current_price>previous:
        normalised=(diff-long_tp_mean)/long_tp_std
        mean=long_tp_mean
        std=long_tp_std
        indicator=True
        
    elif state=='short' and current_price<previous:
        normalised=(diff-short_tp_mean)/short_tp_std
        mean=short_tp_mean
        std=short_tp_std
        #indicator=True
    
    return norm.cdf(normalised)>0.85
    #if not(norm.cdf(normalised)>0.85):
    #    print('no profit taken with probabilistic model: ')
    #    print('State: %s, Diff: %s, mean: %s, std: %s, p-value= %s' % (state, diff, mean, std, norm.cdf(normalised)))

    #print('indicator=',indicator)
    return indicator

def transfer_to_savings(amount):
    Savings._post('subaccounts/transfer', {
        "coin":"USD",
        "size":amount,
        "source":"main",
        "destination":"Savings"
    })

long_tp_mean=None
long_tp_std=None
short_tp_mean=None
short_tp_std=None

position=ShortTerm.get_position('ETH-PERP',True)

total_runtime=0
start_time=time.time()
start_minute=dt.datetime.now().minute

if position==None or position['size']==0:
    string = 'No position, starting state: neutral'
    #precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH-PERP',ftx.fetch_markets()))['precision']['amount']))))
    hourly=price.get_price_data('1h',symbol='ETH-PERP')
    minute=price.get_price_data('1m',symbol='ETH-PERP')
    current_price=minute.iloc[-1]['close']
    trend=chart.identify_trend(hourly,minute,2,24)
    trade_capital=get_free_balance()
    position_size=round(trade_capital/current_price,3)
    if trend=='uptrend':
        ftx.create_order('ETH-PERP','market','buy',position_size)
        state='long'
        entry=current_price
        string='No position, opening long'
    elif trend=='downtrend':
        ftx.create_order('ETH-PERP','market','sell',position_size)
        state='short'
        entry=current_price
        string='No position, opening short'
    else:
        state='neutral'


elif position['side']=='buy':
    entry=float(position['recentBreakEvenPrice'])
    position_size=float(position['size'])
    PnL=float(position['recentPnl'])
    string = "long from % s, current PnL: % s" % (entry, PnL)
    state='long'
elif position['side']=='sell':
    entry=float(position['recentBreakEvenPrice'])
    position_size=float(position['size'])
    PnL=float(position['recentPnl'])
    string = "short from % s, current PnL: % s" % (entry, PnL)
    state='short'

minute=price.get_price_data('1m',symbol='ETH-PERP')
channel=chart.h_l_channel(minute,60)
update_model('neutral',minute,channel)
print(long_tp_mean,long_tp_std, short_tp_mean, short_tp_std)
print(string)
total_runtime=total_runtime+(time.time()-start_time)
print('Total runtime: ', total_runtime)
def run():
    global state
    global trade_capital
    global entry
    global total_runtime
    global start_minute
    start_time=time.time()
    output_string=''
    hourly=price.get_price_data('1h',symbol='ETH-PERP')
    minute=price.get_price_data('1m',symbol='ETH-PERP')
    trend=chart.identify_trend(hourly,minute,6,16)
    current_price=minute.iloc[-1]['close'].item()
    
    #for taking small profits
    channel=chart.h_l_channel(minute,60)
    previous_high=channel.iloc[-1]['high'].item()
    previous_low=channel.iloc[-1]['low'].item()
    now=dt.datetime.now()

    if now.hour == 12 and now.minute==5: #at 12:05 everyday it should reset
        update_model(state,minute,channel)

    if state!='neutral':
        
        position=ShortTerm.get_position('ETH-PERP',True)
        entry=float(position['recentBreakEvenPrice'])
        position_size=float(position['size'])
        PnL=float(position['recentPnl'])
        balance=get_total_balance()
        #print("Current price: % s, PnL: % s" % (str(current_price),PnL))
        percentage_profit=(PnL/balance)*100
        if percentage_profit>0:
            tp_amount=round((np.log(percentage_profit+0.7)/20)*position_size,3)

    # check if profits need to be taken
    if state=='long':
        if tp_indicator(state,previous_high, current_price) and percentage_profit>0.3:
            try:
                ftx.create_limit_sell_order('ETH-PERP',tp_amount,current_price)
                print('tp_amount: %s' % (tp_amount))
                output_string='Profit taken'
            except:
                print(dt.datetime.now())
                print('Failed to tp, tp_amount: %s, position_size: %s' % (tp_amount,position_size))
            
            position=ShortTerm.get_position('ETH-PERP',True)
            position_size=float(position['size'])
            
    elif state=='short':
        if tp_indicator(state, previous_low, current_price) and percentage_profit>0.3:
            try:
                ftx.create_limit_buy_order('ETH-PERP',tp_amount,current_price)
                print('tp_amount: %s' % (tp_amount))
                output_string='Profit taken'
            except:
                print(dt.datetime.now())
                print('Failed to tp, tp_amount: %s, position_size: %s' % (tp_amount,position_size))
            
            position=ShortTerm.get_position('ETH-PERP',True)
            position_size=float(position['size'])
            


    if trend == 'uptrend' and state != 'long':

        output_string='flip long @ '+ str(current_price)+' :'+dt.datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
        if state=='short':#close position
            ftx.create_order('ETH-PERP','market','buy',position_size)
            profit=1-current_price/entry
            balance=get_free_balance()
            trade_capital=get_free_balance()

        position_size=round(trade_capital/current_price,3)

        ftx.create_order('ETH-PERP','market','buy',position_size)
        state='long'
        entry=current_price

    elif trend == 'downtrend' and state != 'short':
        output_string='flip short @ '+ str(current_price)+' :'+dt.datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
        if state=='long':#close position
            ftx.create_order('ETH-PERP','market','sell',position_size)
            profit=current_price/entry - 1
            balance=get_free_balance()
            trade_capital=get_free_balance()

        position_size=round(trade_capital/current_price,3)

        ftx.create_order('ETH-PERP','market','sell',position_size)
        state='short'
        entry=current_price

    if output_string!='':
        print(dt.datetime.now())
        print(output_string)
        append_new_line('ETH_min_log.txt',output_string)


    time_till_next_min=60-time.time()%60-1
    total_runtime=total_runtime+(time.time()-start_time)
    if now.minute==start_minute:
        print('Total runtime: ',total_runtime)
    time.sleep(time_till_next_min-1)

    

print('starting main loop')
#sleep until just before the next min
sleeping_time=60-time.time()%60-1
print('sleeping for ', round(sleeping_time))
scheduler=Scheduler()
scheduler.minutely(dt.time(second=1), run)
print(scheduler)
time.sleep(sleeping_time)

while True:
    scheduler.exec_jobs()