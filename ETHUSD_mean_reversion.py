import ccxt
import price_data as price
import chart
import time
import schedule
import numpy as np
from datetime import datetime
from ftx_client import FtxClient

ftx_ccxt = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

ftx_ccxt.headers = {'FTX-SUBACCOUNT':'MeanReversion'}

main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='MeanReversion')

long_term_period=100
atr_period=6
channel_period=4
sl=None

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
    return True, 'sell'
  elif state=='short' and (current_price<current_channel['low']).all():
    return True, 'buy'
  else:
    return False,''

def price_hit(candle,price):
    return candle['high']>price and candle['low']<price

position=MeanReversion.get_position('ETH-PERP',True)
position_size=float(position['size'])
if position_size==0:
    print('No position, starting state: neutral')
    precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx_ccxt.fetch_markets()))['precision']['amount']))))
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    state='neutral'
    trade_capital=get_free_balance()
    position_size=round(trade_capital/hourly.iloc[-1]['close'],precision)

elif position['side']=='buy':
    print('starting state: long')
    state='long'
elif position['side']=='sell':
    print('starting state: short')
    state='short'

def run():
    global state
    global sl
    print(datetime.now())
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    previous_candle=hourly.iloc[-2]
    current_price=hourly.iloc[-1]['close']
    long_term_ema=chart.get_ema(hourly,long_term_period,False)
    ma_gradient=chart.get_gradient(long_term_ema)
    channel=chart.ma_channel(hourly,channel_period)
    current_channel=channel.iloc[-1]
    atr=chart.get_atr(hourly,atr_period)
    current_atr=atr.iloc[-1]
    channel_low=current_channel['low']
    channel_high=current_channel['high']
    current_gradient=ma_gradient.iloc[-1]

    position=MeanReversion.get_position('ETH-PERP',True)
    position_size=float(position['size'])
    active_trade=position_size!=0

    if active_trade:
      print('Active trade. ')
      print('Channel: %s, open price: %s' % ((str(channel_high)+', '+str(channel_low)), current_price))
      PnL=float(position['recentPnl'])
      entry=float(position['recentBreakEvenPrice'])
      #check for conditions to close trade
      outcome, side = check_close_trade(state,current_price,current_channel)
      if outcome:
        ftx_ccxt.create_order('ETH-PERP','market',side,position_size)
        state=='neutral'
        MeanReversion.cancel_orders()
        active_trade=False
      else:
        print('Trade still active')
    else:
      #check if sl was hit
      if sl!=None:
        if price_hit(previous_candle,sl):
          sl=None
          print('Stop loss hit')
          append_new_line('ETH_meanReversion_log.txt','Stop loss hit.')

      position_size=round((get_free_balance())/current_price,precision)

      if current_gradient>0 and current_price<channel_low:
          output_string='long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
          ftx_ccxt.create_order('ETH-PERP','market','buy',position_size)
          #ftx_ccxt.create_limit_buy_order('ETH-PERP',position_size,current_price)
          sl=current_price-0.5*current_atr
          trigger=current_price-0.49*current_atr
          risk=abs(sl/current_price -1 )
          if (risk<=0.03):
            MeanReversion.place_conditional_order('ETH-PERP','sell',position_size,'stop',limit_price=sl,trigger_price=trigger)
            state='long'
      elif current_gradient<0 and current_price>channel_high:
          output_string='short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
          ftx_ccxt.create_order('ETH-PERP','market','sell',position_size)
          sl=current_price+0.5*current_atr
          trigger=current_price+0.49*current_atr
          risk=abs(sl/current_price -1 )
          if (risk<=0.03):
            MeanReversion.place_conditional_order('ETH-PERP','buy',position_size,'stop',limit_price=sl,trigger_price=trigger)
            state='short'
      else:
        output_string=''
      if output_string!='':
          append_new_line('ETH_meanReversion_log.txt',output_string)
          print(output_string)
      else:
        print('no change')


    time_till_next_hour=3600-time.time()%3600
    time.sleep(time_till_next_hour-5)

print('Starting main loop')
#sleep until just before the next hour
sleeping_time=3600-time.time()%3600 -5
print('sleeping for ', round(sleeping_time/60))
time.sleep(sleeping_time)
schedule.every().hour.at("00:01").do(run)
while True:
    schedule.run_pending()
