import ccxt
import price_data as price
import chart

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

daily=price.get_price_data('1d',symbol='ETH/USD')
hourly=price.get_price_data('1h',symbol='ETH/USD')
state=chart.identify_trend(daily,hourly)

while state != 'neutral':
    print('starting conditions not met')
    pass

while True:

    daily=price.get_price_data('1d',symbol='ETH/USD')
    hourly=price.get_price_data('1h',symbol='ETH/USD')
    trend=chart.identify_trend(daily,hourly)

    trade_capital=10

    usd_balance=float(list(filter(lambda x: x['coin']=='USD',ftx.fetch_balance()['info']['result']))[0]['total'])
    position=next(filter(lambda x: x['future']=='ETH-PERP',ftx.fetch_positions()))
    position_size=trade_capital/hourly.iloc[-1]['close']

    if trend == 'uptrend' and state != 'long':
        print('flip long')
        # if state=='short':#close position
        #     ftx.create_order('ETH-PERP','market','buy',position_size)
        # ftx.create_order('ETH-PERP','market','buy',position_size)
    elif trend == 'downtrend' and state != 'short':
        print('flip short')
        # if state=='long':#close position
        #     ftx.create_order('ETH-PERP','market','sell',position_size)
        # ftx.create_order('ETH-PERP','market','sell',position_size)
    else:
        print('neutral')