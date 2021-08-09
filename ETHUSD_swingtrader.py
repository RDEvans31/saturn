import ccxt
import price_data as price
import chart
import time
import schedule
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
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='MeanReversion')

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

def transfer_to_savings(amount):
    Savings._post('subaccounts/transfer', {
        "coin":"USD",
        "size":amount,
        "source":"main",
        "destination":"Savings"
    })

# def check_starting_conditions():
#     global state
#     print('Checking starting conditions')
#     daily=price.get_price_data('1d',symbol='ETH/USD')
#     hourly=price.get_price_data('1h',symbol='ETH/USD')
#     if state=='neutral':
#         state=chart.identify_trend(daily,hourly,2,24) #MANUALLY CHANGE IF CURRENLT HAS OPEN POSITION
#     if (state!='neutral' and position_size==0.0):
#         print('starting conditions not met')
#     else:
#         return schedule.CancelJob


position=main.get_position('ETH-PERP',True)


if position==None or position['size']==0:
    string = 'No position, starting state: neutral'
    #precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx.fetch_markets()))['precision']['amount']))))
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    current_price=hourly.iloc[-1]['close']
    trend=chart.identify_trend(daily,hourly,2,24)
    trade_capital=get_free_balance()*1.5
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

print(string)

def run():
    global state
    global trade_capital
    global entry
    print(datetime.now())
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    trend=chart.identify_trend(daily,hourly,2,24)
    current_price=hourly.iloc[-1]['close']
    #for taking small profits
    bb=chart.get_bb(hourly,20,2.5).iloc[-1]
    short_term_gradient=chart.get_gradient(chart.get_sma(hourly,20,False)).iloc[-1]

    if state!='neutral':
        position=main.get_position('ETH-PERP',True)
        entry=float(position['recentBreakEvenPrice'])
        position_size=float(position['size'])
        PnL=float(position['recentPnl'])
        balance=get_total_balance()
        percentage_profit=(PnL/balance)*100
        tp_amount=round(np.log(percentage_profit)/100,2)
    #check if profits need to be taken
    if state=='long':
        if (short_term_gradient>0).all() and (bb['upper']<current_price).all() and percentage_profit>5:
            ftx.create_order('ETH-PERP','market','sell',tp_amount*position_size)
            position=main.get_position('ETH-PERP',True)
            position_size=float(position['size'])
            output_string='Profit taken'
    elif state=='short':
        if (short_term_gradient<0).all() and (bb['lower']>current_price).all() and percentage_profit>5:
            ftx.create_order('ETH-PERP','market','buy',tp_amount*position_size)
            position=main.get_position('ETH-PERP',True)
            position_size=float(position['size'])
            output_string='Profit taken'


    if trend == 'uptrend' and state != 'long':

        output_string='flip long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
        if state=='short':#close position
            ftx.create_order('ETH-PERP','market','buy',position_size)
            profit=1-current_price/entry
            balance=get_free_balance()
            if profit>0:
                amount=0.2*profit*balance
                transfer_to_savings(amount)
            trade_capital=get_free_balance()*1.5

        position_size=round(trade_capital/current_price,3)

        ftx.create_order('ETH-PERP','market','buy',position_size)
        state='long'
        entry=current_price

    elif trend == 'downtrend' and state != 'short':
        output_string='flip short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
        if state=='long':#close position
            ftx.create_order('ETH-PERP','market','sell',position_size)
            profit=current_price/entry - 1
            balance=get_free_balance()
            if profit>0:
                amount=0.2*profit*balance
                transfer_to_savings(amount)
            trade_capital=get_free_balance()*1.5

        position_size=round(trade_capital/current_price,3)

        ftx.create_order('ETH-PERP','market','sell',position_size)
        state='short'
        entry=current_price

    else:
        output_string=''
        print('no change. state: ' ,state)
    if output_string!='':
        print(output_string)
        append_new_line('ETH_swingtrader_log.txt',output_string)
    print("Current price: % s, PnL: % s" % (str(current_price),PnL))

    time_till_next_hour=3600-time.time()%3600
    time.sleep(time_till_next_hour-5)

# schedule.every().minute.at(":01").do(check_starting_conditions)
# while state!='neutral' and position_size==0.0:
#     schedule.run_pending()
    #scheduled to run the job every hour
print('starting main loop')
# schedule.clear()
#sleep until just before the next hour
sleeping_time=3600-time.time()%3600 -5
print('sleeping for ', round(sleeping_time/60))
time.sleep(sleeping_time)
schedule.every().hour.at("00:01").do(run)
while True:
    schedule.run_pending()