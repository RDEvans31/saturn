from binance.client import Client
from binance.enums import *
import user

symbols=['XRPUSDT','ETHUSDT','WAVESUSDT','XTZUSDT','DOTUSDT','IOTAUSDT','OMGUSDT']
viable_trades=[]
client=user.client

def get_viable_trades():
    for symbol in symbols:
        kline=client.get_historical_klines(symbol,Client.KLINE_INTERVAL_5MINUTE,'4 hours ago')
        highs=list(map(lambda x:x[2],kline))
        lows=list(map(lambda x:x[3],kline))
        top=float(max(highs))
        bottom=float(min(lows))
        if bottom>top*0.99 and bottom<top*0.995:
            trade=(symbol,top,bottom)
            viable_trades.append(trade)
    return viable_trades
