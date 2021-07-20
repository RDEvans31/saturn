import ccxt
import price_data as price
import pandas as pd
import chart
import time
import math

# import schedule

class Trade:
    def __init__(self,time,side,tp,entry,sl):
        self.time=time
        self.side=side
        self.tp=tp
        self.sl=sl
        self.entry=entry

    def __str__(self):
        return " % s @ % s, tp: % s, entry: % s, sl: % s " % (self.side, self.time, self.tp, self.entry, self.sl) 

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})


# trade_capital=10
# position_size=trade_capital/minute.iloc[-1]['close']

def engulfing(candles):
    previous_two=candles.iloc[-3:-1]
    candle1=previous_two.iloc[0]
    candle2=previous_two.iloc[1]
    if candle1['close']<candle1['open'] and candle2['close']>candle2['open'] and abs(candle2['close']-candle2['open'])>abs(candle1['close']-candle1['open']):
        return 'bullish'
    elif candle1['close']>candle1['open'] and candle2['close']<candle2['open'] and abs(candle2['close']-candle2['open'])>abs(candle1['close']-candle1['open']):
        return 'bearish'
    else:
        return 'not engulfing'

def trade_conditions(candles,ema,rsi):
    current_price=candles[-1]['close']
    if current_price>ema and engulfing(candles)=='bullish' and rsi>50:
        return 'long'
    elif current_price<ema and engulfing(candles)=='bearish' and rsi<50:
        return 'short'

    

def run():
    minute=price.get_price_data('1m',symbol='BTC/USD')
    ema=chart.get_ema(200)
    


while True:
    minute=price.get_price_data('1m',symbol='BTC/USD')
    current_time=time.time()
    datetime=pd.to_datetime(current_time, unit='ms')
    current_price=minute.iloc[-1]['close']
    rsi=chart.get_rsi(minute,20).iloc[-1]
    ema=chart.get_rsi(minute,200).iloc[-1]
    atr=chart.get_atr(minute).iloc[-1]
    if trade_conditions(minute,ema,rsi)=='long':
        entry=current_price
        tp=entry+4*atr
        sl=entry-2*atr
        trade=Trade(datetime,'buy',tp,entry,sl)
        print(trade)
    elif trade_conditions(minute,ema,rsi)=='short':
        entry=current_price
        tp=entry-4*atr
        sl=entry+2*atr
        trade=Trade(datetime,'sell',tp,entry,sl)
        print(trade)
    time.sleep(61-(round(time.time(),0))%60)


