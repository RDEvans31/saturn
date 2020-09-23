from binance.client import Client
import time
#connected to actual binance account
client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 
#client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
# client.API_URL = 'https://testnet.binance.vision/api' 

class User:
    def __init__(self,client):
        self.client = client
        self.futures_account = FuturesAccount(client)

    def show(self):
        self.futures_account.show()

class FuturesAccount:
    def __init__(self,client):

        open_orders = []
        futures_open_positions=[]

        futures_open_positions_unfiltered = self.get_futures_positions(client.futures_position_information())
        open_orders_unfiltered = list(filter(lambda x: x['status']=="NEW" or x['status']=="FILLED",client.futures_get_all_orders(limit = 5)))
        
        for position in futures_open_positions_unfiltered:
            pos_object = Position(position)
            futures_open_positions.append(pos_object)

        for order in open_orders_unfiltered:
            order_object = Order(order)
            open_orders.append(order_object)
        
        self.balance = client.futures_account_balance()
        self.futures_open_positions = futures_open_positions
        self.open_orders = open_orders
        self.trade_amount = 0.1*self.balance
    
    def get_futures_positions(self,position_info):
        open_positions = list(filter(lambda x: float(x['positionAmt'])!=0,position_info))
        return open_positions
        
    def show(self):

        print(self.balance)
        print(list(map(lambda x: x.__dict__, self.futures_open_positions)))
        print(list(map(lambda x: x.__dict__, self.open_orders)))
        
class Order:
    def __init__(self,orderDict):
        print(orderDict)
        self.id = orderDict['orderId']
        self.symbol = orderDict['symbol']
        self.type = orderDict['type']
        self.price = self.getPrice(self.type,orderDict)
        self.status = orderDict['status']
        self.side = orderDict['side']
        if (self.type == 'STOP'):
            self.stopPrice = orderDict['stopPrice']
    
    def getPrice(self,orderType,orderDict):
        print(orderDict)
        switcher = {
            'MARKET': lambda orderDict: float(orderDict.get('avgPrice')),
            'LIMIT': lambda orderDict: float(orderDict.get('price')),
            'STOP': lambda orderDict: float(orderDict.get('price')),
        }
        return switcher.get(orderType)

class Position:
    def __init__(self,posDict):
        self.symbol = posDict['symbol']
        self.position_amount = float(posDict['positionAmt'])
        self.entry = float(posDict['entryPrice'])
        self.current_price = float(posDict['markPrice'])
        self.pnl = float(posDict['unRealizedProfit'])
        self.liq_price = float(posDict['liquidationPrice'])
        self.lev = int(posDict['leverage']) 


#testnet does not support futures




account = User(client)
account.show()
# for x in range(1,5):
#     print("Updating")
#     time.sleep(2)
#     account = User(client)
#     print(account.futures_open_positions)

