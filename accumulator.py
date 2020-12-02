import user

account = user.User()
client=user.client

#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 

class Investment:
    def __init__(self,symbol,current_amount,percentage_exposed):
        pass
        


pairs=[
        {
            'symbol':'XRPUSDT',
            'recurring_amount':10, 
        }
    ]
for currency in pairs:
    current_price = float(list(filter(lambda x : x['symbol'] == currency['symbol'], client.get_all_tickers()))[0]['price'])
    symbol=currency['symbol']
    quantity=current_price*currency['recurring_amount']
    price=current_price
    print(symbol,quantity,price)
    # order = client.order_limit_buy(
    #     symbol=currency['symbol'],
    #     quantity=current_price*currency['recurring_amount'],
    #     price=current_price
    #     )



