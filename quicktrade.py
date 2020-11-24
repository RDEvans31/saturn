import user
import time
import json
import trader
import pyinputplus as pyip
from binance import exceptions

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

#DEAL WITH PRECISION

symbol = str(input('Symbol: '))
current_price = float(list(filter(lambda x : x['symbol'] == symbol, user.client.get_all_tickers()))[0]['price'])
side = decide_side(pyip.inputChoice(prompt='BUY or SELL (b or s): ',choices=['b','s']))
fraction_to_trade = pyip.inputFloat(prompt='Enter portion to trade (eg. 0.1): ',max=1,greaterThan=0)
print("Current price: ", current_price)
entry = float(input('Entry: '))
#sl = float(input('Stop loss: '))
#tp_array = list(map(lambda x: float(x),input("Enter take profit points (seperated by comma): ").split(',')))
leverage = int(input("Enter leverage for trade: "))

#creating trade

trade = trader.TrailingScalp(side = side,percent_amount = fraction_to_trade,symbol = symbol,entry = entry, leverage = leverage)
print(trade.__dict__)
confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
if confirm == 'yes':
    trade.setup_trade()
    # try:
    #     trade.setup_trade()
    # except exceptions.BinanceAPIException:
    #     #keep track of trade status, when entered, create stop loss and trailing profit
    #     print ('API error')
    
else:
    print('Trade cancelled. ')

#trading_pairs = user.futures_account.futures_open_positions
