from binance.client import Client
import user
import time
import json
import trader
import pyinputplus as pyip

client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 

# from binance.websockets import BinanceSocketManager
# from twisted.internet import reactor

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

print('Enter trade')


side = decide_side(pyip.inputChoice(prompt='BUY or SELL (b or s): ',choices=['b','s']))
symbol = str(input('Symbol: '))
current_price = client.get_avg_price(symbol=symbol)
info = client.get_symbol_info(symbol=symbol)
print("Current price: ", current_price)
fraction_to_trade = pyip.inputFloat(prompt='Enter portion to trade (eg. 0.1): ',max=1,greaterThan=0)
entry = float(input('Entry: '))
sl = float(input('Stop loss: '))
tp_array = list(map(lambda x: float(x),input("Enter take profit points (seperated by comma): ").split(',')))
leverage = int(input("Enter leverage for trade: "))

#creating trade

trade = trader.QuickTrade(side = side,percent_amount = fraction_to_trade,symbol = symbol,entry = entry,sl = sl,tp_array = tp_array, leverage = leverage)
print(trade.__dict__)
confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
if confirm == 'yes':
    trade.setup_trade()
else:
    print('Trade cancelled. ')

#trading_pairs = user.futures_account.futures_open_positions
