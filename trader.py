from binance.client import Client
import time

client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
client.API_URL = 'https://testnet.binance.vision/api' 
# testnet url

from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

def readPrice(msg):
    ''' define how to process incoming WebSocket messages '''
    print(msg)
    # if msg['e'] != 'error':
    #     print(msg)
    #     # price['last'] = msg['c']
    #     # if entry < float(price['last']):
    #     #     print('buy')
    #     #     trade['pair'] = tradingPair
    #     #     trade['entered'] = True
    #     #     tradeActive(trade) 
    # else:
    #     price['error'] = True

def tradeActive(t):
    while trade['entered']:
        time.sleep(5)
        print('trade active')
    return

price = {'error' : False} 
trade = {'pair' : None, 'entered' : False}
bsm = BinanceSocketManager(client)
tradingPair = 'ETHUSDT' #test
entry = 365 #test
conn_key = bsm.start_multiplex_socket(['ethusdt@miniTicker','btcusdt@miniTicker','xrpusdt'],readPrice)
bsm.start()
