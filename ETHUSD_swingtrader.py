import ccxt
import price_data as price
from scipy.stats import norm
import chart
import time
from scheduler import Scheduler
import numpy as np
from datetime import datetime
from ftx_client import FtxClient

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')

def get_free_balance():
    return float(next(filter(lambda x:x['coin']=='USD', main.get_balances()))['free'])

def get_total_balance():
  return float(next(filter(lambda x:x['coin']=='USD', main.get_balances()))['total'])

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

def update_model(price_data,channel_full):
    print('Updating model') #this will need to be routinely called to adjust for recent volatility

    global long_tp_mean
    global long_tp_std
    global short_tp_mean
    global short_tp_std
    diff=None
    channel=channel_full.iloc[1100:]
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

def tp_indicator(state,previous,current_price):
    global long_tp_mean
    global long_tp_std
    global short_tp_mean
    global short_tp_std
    diff=abs(current_price-previous)/current_price
    normalised=0
    if state=='long' and current_price>previous:
        normalised=(diff-long_tp_mean)/long_tp_std
    elif state=='short' and current_price<previous:
        normalised=(diff-short_tp_mean)/short_tp_std
    return norm.cdf(normalised)>0.85

def sl_trigger(state, previous, current_price):
    if state=='long' and current_price>previous:
        return True
    elif state=='short' and current_price<previous:
        return True
    else:
        return False

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

# print(long_tp_mean,long_tp_std, short_tp_mean, short_tp_std)
# model_updated=False

output_string=''
stop_loss=False
daily=price.get_price_data('1d',symbol='ETH/USD')
current_price=daily.iloc[-1]['close'].item()
trend=chart.identify_trend(daily,7)
position=main.get_position('ETH-PERP',True)
position_size=float(position['size'])
active_trade=position_size!=0

if active_trade:
    entry=float(position['recentBreakEvenPrice'])
    PnL=float(position['recentPnl'])
    balance=get_total_balance()
    percentage_profit=(PnL/balance)*100
    if percentage_profit>0:
        tp_amount=round(np.log(percentage_profit)/20,2)
    stop_loss=len(main.get_conditional_orders())>0

    if position['side']=='buy':
        state='long'
    else:
        state='short'
else:
    state='neutral'

#for taking small profits
channel=chart.h_l_channel(daily,12)
previous_high=channel.iloc[-2]['high'].item()
previous_low=channel.iloc[-2]['low'].item()

# if datetime.now().weekday()%2==0 and not(model_updated):
#     update_model(daily,channel)
#     model_updated=True
# elif not(datetime.now().weekday()%2==0):
#     model_updated=False

#check if profits need to be taken and if stop loss can be set
# if state=='long':
#     if not(stop_loss) and current_price>entry and sl_trigger(state,previous_high,current_price):
#         main.place_conditional_order('ETH-PERP','sell',position_size,'stop',trigger_price=np.mean([entry,current_price]))

#     if tp_indicator(state,previous_high, current_price) and percentage_profit>1:
#         try:
#             ftx.create_limit_sell_order('ETH-PERP',tp_amount,current_price)
#             print('tp_amount: %s' % (tp_amount))
#             output_string='Profit taken'
#         except:
#             print(datetime.now())
#             print('Failed to tp, tp_amount: %s, position_size: %s' % (tp_amount,position_size))
        
#         position=main.get_position('ETH-PERP',True)
#         position_size=float(position['size'])
# elif state=='short':
#     if not(stop_loss) and current_price<entry and sl_trigger(state,previous_low,current_price):
#         main.place_conditional_order('ETH-PERP','buy',position_size,'stop',trigger_price=np.mean([entry,current_price]))
    
#     if tp_indicator(state, previous_low, current_price) and percentage_profit>1:
#         try:
#             ftx.create_limit_buy_order('ETH-PERP',tp_amount,current_price)
#             print('tp_amount: %s' % (tp_amount))
#             output_string='Profit taken'
#         except:
#             print(datetime.now())
#             print('Failed to tp, tp_amount: %s, position_size: %s' % (tp_amount,position_size))
#         position=main.get_position('ETH-PERP',True)
#         position_size=float(position['size'])



if trend == 'uptrend' and state != 'long':

    output_string='flip long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='short':#close position
        main.cancel_orders()
        ftx.create_order('ETH-PERP','market','buy',position_size)
        profit=1-current_price/entry
        balance=get_free_balance()
        if profit>0:
            amount=0.2*profit*balance
            transfer_to_savings(amount)
    trade_capital=get_free_balance()

    position_size=round(trade_capital/current_price,3)

    ftx.create_order('ETH-PERP','market','buy',position_size)
    state='long'
    entry=current_price

elif trend == 'downtrend' and state != 'short':
    output_string='flip short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='long':#close position
        main.cancel_orders()
        ftx.create_order('ETH-PERP','market','sell',position_size)
        profit=current_price/entry - 1
        balance=get_free_balance()
        if profit>0:
            amount=0.2*profit*balance
            transfer_to_savings(amount)
    trade_capital=get_free_balance()

    position_size=round(trade_capital/current_price,3)

    ftx.create_order('ETH-PERP','market','sell',position_size)
    state='short'
    entry=current_price

if output_string!='':
    print(output_string)
    append_new_line('ETH_swingtrader_log.txt',output_string)
if state != 'neutral':
    print(datetime.now())
    print("Date: %s, Current price: % s, PnL: % s" % (str(datetime.now()),str(current_price),PnL))
