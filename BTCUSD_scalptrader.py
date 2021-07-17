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


# trade_capital=10
# position_size=trade_capital/minute.iloc[-1]['close']

def engulfing(candles):
    previous_two=candles.iloc[-3:-1]
    candle1=candle.iloc[0]
    candle2=candle.iloc[1]
    if candle1['close']<candle1['open'] and candle2['close']>candle2['open'] and abs(candle2['close']-candle2['open'])>abs(candle1['close']-candle1['open']):
        return 'bullish'
    elif candle1['close']>candle1['open'] and candle2['close']<candle2['open'] and abs(candle2['close']-candle2['open'])>abs(candle1['close']-candle1['open']):
        return 'bearish'
    else:
        return 'not engulfing'

def trade_conditions(candles,ema):
    current_price=candles[-1]['close']
    rsi_bullish=chart.get_rsi(candles,20)>50
    if current_price>ema and engulfing(candles)=='bullish' and rsi_bullish:
        return 'long'
    elif current_price<ema and engulfing(candles)=='bearish' and not(rsi_bullish):
        return 'short'

    

def run():
    minute=price.get_price_data('1m',symbol='ETH/USD')
    ema=chart.get_ema(200)
    


# while True:
#     schedule.run_pending()
minute=price.get_price_data('1m',symbol='ETH/USD')
print(minute.iloc[-3:])