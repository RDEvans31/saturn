from binance.client import Client
import user
import time

client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
client.API_URL = 'https://testnet.binance.vision/api' 
# testnet url

from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

class Trade: 
    def __init__(self,side,t,symbol,entry,sl,tp_array):
        self.entry = entry
        self.side = side
        self.type = t
        self.symbol = symbol
        self.sl = sl
        self.tp = tp_array
        self.entered = False

    def create_entry_order(self):
        # if self.type == LIMIT:

        # else if 
    def set__tp(self):

    def set_sl(self):

def readPrice(msg):
    ''' define how to process incoming WebSocket messages '''

    if 'e' in msg: #msg['e'] == 'error':
        print(msg)
        #reconnect
    else:
        for stream in msg:
            if (stream['stream'] == tradingPair):
                print(stream)
        # price['last'] = msg['c']
        # if entry < float(price['last']):
        #     print('buy')
        #     trade['pair'] = tradingPair
        #     trade['entered'] = True
        #     tradeActive(trade) 



bsm = BinanceSocketManager(client, user_timeout = 20)
trading_pairs = 
conn_key = bsm.start_multiplex_socket(['ethusdt@miniTicker','btcusdt@miniTicker','xrpusdt@miniticker'],readPrice)
bsm.start()
