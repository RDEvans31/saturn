from binance.client import Client
import user
import time
import trader

client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 

from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

# def readPrice(msg):
#     ''' define how to process incoming WebSocket messages '''

#     if 'e' in msg: #msg['e'] == 'error':
#         print(msg)
#         #reconnect
#     else:
#         for stream in msg:
#             if (stream['stream'] == tradingPair):
#                 print(stream)
        # price['last'] = msg['c']
        # if entry < float(price['last']):
        #     print('buy')
        #     trade['pair'] = tradingPair
        #     trade['entered'] = True
        #     tradeActive(trade) 

def decide_side(string):
    if string=='b':
        return 'BUY'
    elif string == 's':
        return 'SELL'


my_account = user.User()

print('Enter trade:')
side = decide_side(input('BUY or SELL (b or s): '))
symbol = input('Symbol: ')
fraction_to_trade = float(input('Enter portion to trade (eg. 0.1): '))
entry = float(input('Entry: '))
sl = float(input('Stop loss: '))
tp_array = list(map(lambda x: float(x),input("Enter take profit points (seperated by comma): ").split(',')))
leverage = int(input("Enter leverage for trade: "))

#creating trade

trade = trader.QuickTrade(side = side,percent_amount = fraction_to_trade,symbol = symbol,entry = entry,sl = sl,tp_array = tp_array, leverage = leverage)



#trading_pairs = user.futures_account.futures_open_positions
