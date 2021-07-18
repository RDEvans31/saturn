import ccxt
import price_data as price
import chart
import time
import schedule
import numpy as np
import time
from datetime import datetime

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx.fetch_markets()))['precision']['amount']))))
daily=price.get_price_data('1d',symbol='ETH/USD')
hourly=price.get_price_data('1h',symbol='ETH/USD')
state=chart.identify_trend(daily,hourly)
trade_capital=10
position_size=trade_capital/hourly.iloc[-1]['close']
position_size=round(position_size,precision)

def new_hour():
   return int(time.time())/3600 == int(time.time())//3600

def check_starting_conditions():
    global state
    print('checking')
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    state=chart.identify_trend(daily,hourly) #MANUALLY CHANGE IF CURRENLT HAS OPEN POSITION
    if state!='neutral':
        print('starting conditions not met')
    else:
        return schedule.CancelJob



def run():
    global state
    print(datetime.now())
    print('state: ', state)
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    trend=chart.identify_trend(daily,hourly)

    usd_balance=float(list(filter(lambda x: x['coin']=='USD',ftx.fetch_balance()['info']['result']))[0]['total'])
    position=next(filter(lambda x: x['future']=='ETH-PERP',ftx.fetch_positions()))
    position_size=round(float(position['size']),precision)

    if trend == 'uptrend' and state != 'long':
        print('flip long @ '+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S"))
        # if state=='short':#close position
        #     ftx.create_order('ETH-PERP','market','buy',position_size)
        # ftx.create_order('ETH-PERP','market','buy',position_size)
        state='long'
    elif trend == 'downtrend' and state != 'short':
        print('flip short @ '+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S"))
        # if state=='long':#close position
        #     ftx.create_order('ETH-PERP','market','sell',position_size)
        # ftx.create_order('ETH-PERP','market','sell',position_size)
        state='short'

    else:
        print('neutral after check')
    
    time_till_next_hour=3600-time.time()%3600
    time.sleep(time_till_next_hour-5)

print('runnning')
schedule.every().minute.at(":01").do(check_starting_conditions)
print(state)
while state!='neutral':
    schedule.run_pending()
    #scheduled to run the job every hour
print('state netral, starting')
schedule.clear()
#sleep until just before the next hour
sleeping_time=3600-time.time()%3600 -5
print('sleeping for ', round(sleeping_time/60))
time.sleep(sleeping_time)
schedule.every().hour.at("00:01").do(run)
while True:
    schedule.run_pending()