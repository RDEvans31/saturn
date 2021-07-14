import ccxt
import price_data as price
import numpy as np

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

def submit_order(symbol,current_price,quantity):
    
    return ftx.create_limit_buy_order(symbol,current_price,quantity)


pairs=[
        {
            'asset' : 'XRP',
            'symbol':'XRP/USD',
            'recurring_amount':5, #buy 10 dollars worth everytime this is run
        },
        {
            'asset' : 'ETH',
            'symbol':'ETH/USD',
            'recurring_amount':5, #buy 10 dollars worth everytime this is run
        },
    ]
for currency in pairs:
    current_price = price.get_current_price(currency['symbol'])
    symbol=currency['symbol']
    decimal_places=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx.fetch_markets()))['precision']['amount']))))
    quantity=ftx.decimal_to_precision(currency['recurring_amount']/current_price,precision=decimal_places)
    
    
    print(symbol,quantity,current_price)
    
    # order=submit_order(symbol,price,quantity,5)
    # print(order)



