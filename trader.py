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
        self.symbol = str(symbol)
        self.side = str(side)
        self.type = str(t)
        self.sl = sl
        self.tp = tp_array
        self.entry_id = self.symbol+"entry"
        #check entry order to see if its filled or not
        self.entered = False
        account = User(client)
        self.quantity = account.futures_account.trade_amount * self.entry
        if (not(self.entered)):
            self.create_entry_order()

    def entry_filled_check(self):
        entry_order = user.Order(client.get_order(symbol = self.symbol, order = self.entry_id))
        if (entry_order.status == "FILLED"):
            return True
        else:
            return False

    def create_entry_order(self):
        order = client.futures_create_order(
            newClientOrderId = self.entry_id,
            symbol = self.symbol,
            side = self.side,
            type = 'STOP',
            quantity = self.quantity,
            price = self.entry,
            stopPrice = self.entry,
            timeInForce = GTC,
        )


    def set__tp(self):
        return None
    def set_sl(self):
        if (self.entered):
            
        return None
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
