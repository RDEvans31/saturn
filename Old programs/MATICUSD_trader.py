import ccxt
import price_data as price
import numpy as np
from datetime import datetime


def fetch_position(exchange: ccxt.Exchange):
    request = {
        'showAvgPrice': True,
    }
    try:
        response = exchange.privateGetPositions(exchange.extend(request))
        result = exchange.safe_value(response, 'result', [])
        return next(filter(lambda x: x['future']=='MATIC-PERP',result))
    except:
        return {'size': 0}

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

# HEIKIN ASHI TRADER

ftx_ha_trader = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

ftx_ha_trader.headers = { 'FTX-SUBACCOUNT':'MATIC_TRADING' }

def get_free_balance_ha():
    return float(ftx_ha_trader.fetch_balance()['USD']['free'])

def get_total_balance_ha():
  return float(ftx_ha_trader.fetch_balance()['USD']['total'])

output_string=''
stop_loss=False
weekly=price.get_price_data('1w',symbol='MATIC/USD')
current_price=weekly.iloc[-1]['close'].item()
uptrend=price.convert_data_to_heikin_ashi(weekly).iloc[-1]['Green']
position=fetch_position(ftx_ha_trader)
position_size=float(position['size'])
active_trade=position_size!=0

if active_trade:
    entry=float(position['recentBreakEvenPrice'])
    PnL=float(position['recentPnl'])
    balance=get_total_balance_ha()
    percentage_profit=(PnL/balance)*100
    if percentage_profit>0:
        tp_amount=round(np.log(percentage_profit)/20,2)
    # stop_loss=len(main.get_conditional_orders())>0

    if position['side']=='buy':
        state='long'
    else:
        state='short'
else:
    state='neutral'

if uptrend and state != 'long':

    output_string='flip long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='short':#close position
        ftx_ha_trader.cancel_all_orders()
        ftx_ha_trader.create_order('MATIC-PERP','market','buy',position_size)
        profit=1-current_price/entry
        balance=get_free_balance_ha()

    trade_capital=get_free_balance_ha()
    position_size=round(0.99*(trade_capital/current_price),3)
    ftx_ha_trader.create_order('MATIC-PERP','market','buy',position_size)
    state='long'
    entry=current_price

elif not(uptrend) and state != 'short':
    output_string='flip short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state=='long':#close position
        ftx_ha_trader.cancel_all_orders()
        ftx_ha_trader.create_order('MATIC-PERP','market','sell',position_size)
        profit=current_price/entry - 1
        balance=get_free_balance_ha()
        if profit>0:
            amount=0.2*profit*balance
            # transfer_to_savings(amount)
    trade_capital=get_free_balance_ha()
    position_size=round(0.99*(trade_capital/current_price),3)
    ftx_ha_trader.create_order('MATIC-PERP','market','sell',position_size)
    state='short'
    entry=current_price

if active_trade:
    print("Date: %s, Breakeven: %s, Current price: % s, PnL: % s" % (str(datetime.now()), str(entry),str(current_price),PnL))