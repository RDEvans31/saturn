from binance.client import Client
client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
client.API_URL = 'https://testnet.binance.vision/api' 
# testnet url

from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

def readPrice(msg):
    ''' define how to process incoming WebSocket messages '''
    if msg['e'] != 'error':
        print(msg['s'])
        price['last'] = msg['c']
        if entry < price['last']:
            print('buy')
            bsm.stop_socket(conn_key)
            reactor.stop()
            trade['pair'] = tradingPair
            trade['entered'] = True
            
    else:
        price['error'] = True

price = {'error' : False} 
trade = {'pair' : None, 'entered' : False}
bsm = BinanceSocketManager(client)
tradingPair = input('Enter trading pair: ')
entry = input('Enter entry price (in left side of pairing): ')
conn_key = bsm.start_symbol_ticker_socket(tradingPair, readPrice)
bsm.start()



