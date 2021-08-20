from operator import truediv
import ccxt
import price_data as price
import chart
import time
import schedule
import numpy as np
import pandas as pd
from datetime import datetime
from ftx_client import FtxClient

ftx_ccxt = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

ftx_ccxt.headers = {'FTX-SUBACCOUNT':'Minute_MeanReversion'}

main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Minute_MeanReversion')

long_term_period=15
atr_period=9
channel_period=2
sl=None
sl_multiple=0.3

def get_free_balance():
    return float(next(filter(lambda x:x['coin']=='USD', MeanReversion.get_balances()))['free'])

def get_total_balance():
  return float(next(filter(lambda x:x['coin']=='USD', MeanReversion.get_balances()))['total'])

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

def check_close_trade(state,current_price,current_channel): #returns boolean for closing trade, side of closing order
  if state=='long' and (current_price>current_channel['high']).all():
    return True, 'buy'
  elif state=='short' and (current_price<current_channel['low']).all():
    return True, 'sell'
  else:
    return False,''

def price_hit(candle,price):
    return candle['high']>price and candle['low']<price

position=MeanReversion.get_position('ETH-PERP',True)
position_size=float(position['size'])
active_trade=position_size!=0
if position_size==0:
    print('No position, starting state: neutral')
    #precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx_ccxt.fetch_markets()))['precision']['amount']))))
    minute=price.get_price_data('1m',symbol='ETH-PERP')
    state='neutral'
    trade_capital=get_free_balance()
    position_size=round(trade_capital/minute.iloc[-1]['close'],3)

elif position['side']=='buy':
    print('starting state: long')
    state='long'
elif position['side']=='sell':
    print('starting state: short')
    state='short'

sl=None

def run():
    global state
    global active_trade
    global sl
    minute=price.get_price_data('1m',symbol='ETH-PERP')
    current_price=minute.iloc[-1]['close']
    long_term_ema=chart.get_ema(minute,long_term_period,True)
    ma_gradient=chart.get_gradient(long_term_ema)
    channel=chart.ma_channel(minute,channel_period)
    current_channel=channel.iloc[-1]
    atr=chart.get_atr(minute,atr_period)
    current_atr=atr.iloc[-1]
    channel_low=current_channel['low']
    channel_high=current_channel['high']
    current_gradient=ma_gradient.iloc[-2]

    date=datetime.now()
    # print('Channel: %s, open price: %s, gradient: %s' % ((str(channel_high)+', '+str(channel_low)), current_price, current_gradient.item()))

    position=MeanReversion.get_position('ETH-PERP',True)
    position_size=float(position['size'])
    if active_trade:
      no_orders=len(MeanReversion.get_conditional_orders())==0
      # testing
      # if price_hit(minute.iloc[-1],sl):
      #   active_trade=False
      #   state='neutral'
      #   print('Stop loss hit')
      #   append_new_line('ETH_meanReversion_log_min.txt','Stop loss hit.')
      if no_orders:
        active_trade=False
        state='neutral'
        print('TP hit')
        append_new_line('ETH_meanReversion_log_min.txt','TP hit.')
    active_trade=position_size!=0
    if active_trade:
        print('Active trade. ')
        #check for conditions to close trade
        outcome, side = check_close_trade(state,current_price,current_channel)
        if outcome:
          ftx_ccxt.create_order('ETH-PERP','market',side,position_size)
          print('Position closed with a loss')
          state='neutral'
          MeanReversion.cancel_orders()
          active_trade=False
        else:
          print('Trade still active')
    else:
      position_size=round((get_free_balance())/current_price,3)

      if current_gradient<0 and current_price<channel_low:
          
          sl=current_price-sl_multiple*current_atr
          output_string='long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S") + "sl: "+str(sl)
          risk=abs(sl/current_price -1 )
          try:
            MeanReversion.place_conditional_order('ETH-PERP','buy',position_size,'stop',trigger_price=sl)
            ftx_ccxt.create_order('ETH-PERP','market','sell',position_size)
            active_trade=True
          except:
            print(current_price,sl)
            state='long'
      elif current_gradient<0 and current_price>channel_high:
          
          sl=current_price+sl_multiple*current_atr
          output_string='short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S") + " sl: "+str(sl)
          risk=abs(sl/current_price -1 )
          try:
            MeanReversion.place_conditional_order('ETH-PERP','sell',position_size,'stop',trigger_price=sl)
            ftx_ccxt.create_order('ETH-PERP','market','buy',position_size)
            active_trade=True
          except:
            print(current_price,sl)
            state='short'
      else:
        output_string=''
      if output_string!='':
          append_new_line('ETH_meanReversion_log-min.txt',output_string)
          print(output_string)


    time_till_next_min=60-time.time()%60-1
    time.sleep(time_till_next_min-1)

print('Starting main loop')
#sleep until just before the next hour
sleeping_time=60-time.time()%60-1
print('sleeping for ', round(sleeping_time))
time.sleep(sleeping_time)
schedule.every().minute.at(":01").do(run)
while True:
    schedule.run_pending()
