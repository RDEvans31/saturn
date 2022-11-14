import ccxt
import price_data as price
from scipy.stats import norm
import chart
import numpy as np
from datetime import datetime
symbol_binance='ETH/USDT'
symbol_kucoin_futures='ETH/USDT:USDT'

kucoin = ccxt.kucoinfutures({    
    "apiKey": '6372b12d3671050001314dc3',
    "secret": 'a69adc2e-457d-48a8-907b-d69f8afbbf08',
    'password': 'SaturnApi',})

def get_free_balance():
    return float(kucoin.fetch_balance()['USDT']['free'])

def get_total_balance():
  return float(kucoin.fetch_balance()['USDT']['total'])


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


output_string=''
daily=price.get_price_data('1d',exchange_str='binance',symbol='ETH/USDT')
current_price=daily.iloc[-1]['close'].item()
trend=chart.identify_trend(daily,7)
position=next(filter(lambda x: x['symbol']=='ETH/USDT:USDT', kucoin.fetch_positions()))
position_size=float(position['size'])
active_trade=position_size!=0

if active_trade:

    if position['side']=='short':
        state='short'
    else:
        state='long'
else:
    state='neutral'


# need to try placing and cancelling orders on jupyter notebook (closing and opening positions)
if trend == 'uptrend' and state != 'long':

    output_string='flip long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='short':#close position
        kucoin.cancel_all_orders()
        kucoin.create_order('ETH-PERP','market','buy',position_size)
        profit=1-current_price/entry
        balance=get_free_balance()

    trade_capital=get_free_balance()

    position_size=round(trade_capital/current_price,3)

    # kucoin.create_order('ETH-PERP','market','buy',position_size)
    state='long'
    entry=current_price

elif trend == 'downtrend' and state != 'short':
    output_string='flip short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='long':#close position
        kucoin.cancel_all_orders()
        kucoin.create_order('ETH-PERP','market','sell',position_size)
        profit=current_price/entry - 1
        balance=get_free_balance()
    trade_capital=get_free_balance()

    position_size=round(trade_capital/current_price,3)

    # kucoin.create_order('ETH-PERP','market','sell',position_size)
    state='short'
    entry=current_price

if output_string!='':
    print(output_string)
    append_new_line('ETH_swingtrader_log.txt',output_string)
if state != 'neutral':
    print(datetime.now())
    print("Date: %s, Breakeven: %s, Current price: % s, PnL: % s" % (str(datetime.now()), str(entry),str(current_price), PnL))
