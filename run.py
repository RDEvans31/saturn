from binance.client import Client
import user
import time

client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 
# client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
# client.API_URL = 'https://testnet.binance.vision/api' 
# testnet url

from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

def readPrice(msg):
    ''' define how to process incoming WebSocket messages '''

    if 'e' in msg: #msg['e'] == 'error':
        print(msg)
        #reconnect
    else:
        user = user.User(client)
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
tradingPair = 'ETHUSDT'
trading_pairs = user.futures_account.futures_open_positions
conn_key = bsm.start_multiplex_socket(['ethusdt@miniTicker','btcusdt@miniTicker','xrpusdt@miniticker'],readPrice)
bsm.start()
