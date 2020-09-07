from binance.client import Client
import time
#connected to actual binance account
client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 
#client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
# client.API_URL = 'https://testnet.binance.vision/api' 

class User:
    def __init__(self,client):
        self.client = client
        self.futures_account = client.futures_account()
        self.cash_balance = client.futures_account_balance()
        self.futures_open_positions = get_futures_positions(client.futures_position_information())
        self.open_orders = list(filter(lambda x: x['status']=="NEW",client.futures_get_all_orders()))
    
    def show(self):
        print(self.cash_balance)
        print(self.futures_open_positions)
        print(self.open_orders)

#testnet does not support futures
def get_futures_positions(position_info):
    open_positions = list(filter(lambda x: float(x['positionAmt'])!=0,position_info))
    return open_positions

account = User(client)
print(account)
# for x in range(1,5):
#     print("Updating")
#     time.sleep(2)
#     account = User(client)
#     print(account.futures_open_positions)

