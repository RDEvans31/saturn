from binance.client import Client

#connected to actual binance account
client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 

def get_usdt_balance(account_balance):
    usdt_account = list(filter(lambda x: x['asset']=='USDT',account_balance))[0]
    balance = usdt_account['balance']
    return balance

info = client.get_account()
usdt_balance = get_usdt_balance(client.futures_account_balance())
print(usdt_balance)
