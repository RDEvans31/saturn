import user
import ccxt
from binance.exceptions import BinanceAPIException

account = user.User()
client=user.client

binance = ccxt.binance({
    'apiKey': 'HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK',
    'secret': '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4',
    'timeout': 30000,
    'enableRateLimit': True,
})

phemex = ccxt.phemex({
    'secret' : 'GgWgKUdSCiSirVXS9fmXd4_th-SeXFjMr9g_HmJBgFU2MjQ0ZDMzMy04NmVkLTQ3ZmMtOGNlMC02MDZmZTJjMzEzYWM',
    'enableRateLimit': True,
})
ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 

def lower_precision(n,prec):
    return float( "{:.{prec}f}".format(n, prec=prec-1))

def submit_order(symbol,testprice,quantity,prec):
    print((symbol,quantity,price,prec))
    order=None
    try:
        
        # order=client.create_test_order(
        #     symbol=symbol,
        #     side='BUY',
        #     type='MARKET',
        #     quantity=quantity,
        # )
        order=client.order_market_buy(
            symbol=symbol,
            quantity=quantity,
            )
         
    except BinanceAPIException as e:
        if e.code == -1111:
            new_price=lower_precision(price,prec)
            return submit_order(symbol,quantity,prec-1)

        if e.code == -1013: #quantity is below this notional
            new_quantity=quantity*1.05
            return submit_order(symbol,testprice,new_quantity,prec)
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
            'asset' : 'XRP',
            'symbol':'XRPUSDT',
            'recurring_amount':10, #buy 10 dollars worth everytime this is run
        },
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
    
    order=submit_order(symbol,price,quantity,5)
    print(order)



