import user
from binance.exceptions import BinanceAPIException

account = user.User()
client=user.client

#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 

def lower_precision(n,prec):
    return float( "{:.{prec}f}".format(n, prec=prec-1))

def submit_order(symbol,quantity,prec):
    print((symbol,quantity,price,prec))
    new_price=None
    order=None
    try:
        return client.order_market_buy(
            symbol=symbol,
            quantity=quantity,
            )
         
    except BinanceAPIException as e:
        if e.code == -1111:
            new_price=lower_precision(price,prec)
            return submit_order(symbol,quantity,prec-1)
        # elif e.code == -1013:
        #     new_quantity = lower_precision(quantity,prec)
        #     submit_order(symbol,quantity,new_price,prec-1)
        else:
            print(e)
    
    return order

class Investment:
    def __init__(self,symbol,current_amount,percentage_exposed):
        pass
        


pairs=[
        {
            'symbol':'XRPUSDT',
            'recurring_amount':15, #buy 15 dollars worth everytime this is run
        },
        {
            'symbol': 'WAVESUSDT',
            'recurring_amount': 15,
        }
    ]
for currency in pairs:
    current_price = float(list(filter(lambda x : x['symbol'] == currency['symbol'], client.get_all_tickers()))[0]['price'])
    symbol=currency['symbol']
    price=lower_precision(current_price,5)
    quantity=0
    if price < currency['recurring_amount']:
        quantity=lower_precision(currency['recurring_amount']/price, 2)
    else:
        quantity=lower_precision(currency['recurring_amount']/price, 5)
    # print(symbol,quantity,price)
    
    submit_order(symbol,quantity,5)



