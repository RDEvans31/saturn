import ccxt
import price_data as price
import chart
import time
import math
import schedule

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

daily=price.get_price_data('1d',symbol='ETH/USD')
hourly=price.get_price_data('1h',symbol='ETH/USD')
state=chart.identify_trend(daily,hourly) #MANUALLY CHANGE IF CURRENLT HAS OPEN POSITION

def new_hour():
   return int(time.time())/3600 == int(time.time())//3600


while state != 'neutral' or not(new_hour()): #wait until the state is neutral before begininning to look for trades
    print('starting conditions not met')
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    state=chart.identify_trend(daily,hourly)
    #it's the start of an hour and there is a neutral trend so the program will do nothing when it starts

print('starting conditions met')

trade_capital=10
position_size=trade_capital/hourly.iloc[-1]['close']
precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx.fetch_markets()))['precision']['amount']))))
position_size=round(position_size,precision)

def run():
    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    trend=chart.identify_trend(daily,hourly)

    usd_balance=float(list(filter(lambda x: x['coin']=='USD',ftx.fetch_balance()['info']['result']))[0]['total'])
    position=next(filter(lambda x: x['future']=='ETH-PERP',ftx.fetch_positions()))
    position_size=round(float(position['size'],precision)

    if trend == 'uptrend' and state != 'long':
        print('flip long')
        if state=='short':#close position
            position_size=position['size']
            ftx.create_order('ETH-PERP','market','buy',position_size)
        ftx.create_order('ETH-PERP','market','buy',position_size)
    elif trend == 'downtrend' and state != 'short':
        print('flip short')
        if state=='long':#close position
            ftx.create_order('ETH-PERP','market','sell',position_size)
        ftx.create_order('ETH-PERP','market','sell',position_size)
    else:
        print('neutral')

schedule.every().hour.do(run)

while True:
    schedule.run_pending()
    #scheduled to run the job every hour