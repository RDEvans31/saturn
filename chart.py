from binance.client import Client
from binance.enums import *
import user

symbols=['XRPUSDT','ETHUSDT','WAVESUSDT','LTCUSDT','IOTAUSDT','OMGUSDT','ALGOUSDT']
time_periods=['1 hour ago', '2 hours ago', '3 hours ago','4 hours ago']
viable_trades=[]
client=user.client
open_orders=client.futures_get_open_orders()

# returns true if there are no more open orders for 
def symbol_open_orders(symbol):
    orders=list(filter(lambda x: x['symbol']==symbol, open_orders))
    if len(orders)==0:
        return True
    else:
        return False

def get_viable_trades():
    for symbol in symbols:
        print('Checking:', symbol)
        if symbol_open_orders(symbol):
            trade_found=False
            i=len(time_periods)-1
            while not(trade_found) and i>=0:
                print('Checking: ',time_periods[i])
                kline=[]
                try:
                    kline=client.get_historical_klines(symbol,Client.KLINE_INTERVAL_5MINUTE,time_periods[i])
                except:
                    print("Could not get klines")
                if len(kline)>0:
                    highs=list(map(lambda x:x[2],kline))
                    lows=list(map(lambda x:x[3],kline))
                    top=float(max(highs))
                    bottom=float(min(lows))
                    if bottom>top*0.99 and bottom<top*0.995:
                        trade=(symbol,top,bottom,i)
                        viable_trades.append(trade)
                        trade_found=True 
                        print('Trade found.')
                    else:
                        i=i-1
            if not(trade_found):
                print('Could not find trade for ', symbol)
        else:
            print("There are open orders.")
    return viable_trades

