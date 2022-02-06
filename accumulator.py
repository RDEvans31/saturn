import ccxt
from pandas.core import api
import price_data
import chart
import numpy as np
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from users import users
from datetime import datetime

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True
})

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

def get_limit(symbol, markets):
    return float(next(filter(lambda x:x['symbol']==symbol, markets))['limits']['amount']['min'])

def accumulate(risk, risk_ethbtc, exchange_str, exchange, symbols, buy_amount):
    usd_balance=exchange.fetch_partial_balance('USD')['free']
    gbp_balance=exchange.fetch_partial_balance('GBP')['free']
    markets=exchange.fetch_markets()
    print('USD balance: ', usd_balance)
    if risk>=0.5:
        print('ETHBTC risk level', risk_ethbtc)
        #sell btc
        price=price_data.get_price_data('1m', symbol='BTC/USD')
        try:
            btc_balance=float(exchange.fetch_partial_balance('BTC')['total'])
        except:
            print('No balance for BTC ')
        current_price=price.iloc[-1]['close'].item()
        dynamic_sell_amount=round((-1/(50*(risk-1))), 2)*btc_balance
        limit=get_limit('BTC/USD', markets)
        sell_amount=min(btc_balance,dynamic_sell_amount)
        if sell_amount>=limit:
            exchange.create_limit_sell_order('BTC/USD',sell_amount,current_price)
            print('Sold %s of %s' %(dynamic_sell_amount, 'BTC/USD'))
        else:
            print('No btc to sell')
        usd_amount=sell_amount*current_price
        if risk_ethbtc<0.5: #move those profits over to eth
                usd_balance=exchange.fetch_partial_balance('USD')['free']   
                eth_price=price_data.get_price_data('1m',symbol='ETH/USD')       
                #buy
                current_eth_price=eth_price.iloc[-1]['close'].item()
                buy_amount=usd_amount/current_eth_price
                if buy_amount<usd_balance:
                    print('Buying eth with BTC profits')
                    amount_to_buy=round(buy_amount/current_eth_price,3) #eth has a precision of 0.001
                    limit=get_limit('ETH/USD', markets)
                    if amount_to_buy>limit:
                        exchange.create_limit_buy_order('ETH/USD',amount_to_buy,current_price)
                        print('Bought %s of %s' %(amount_to_buy, 'ETH/USD'))
                    elif limit<usd_balance:
                        print('Amount not above limit: %s, %s' % (limit,amount_to_buy))
                        exchange.create_limit_buy_order('ETH/USD',limit,current_price)
                        print('Bought %s of %s' %(limit, 'ETH/USD'))
                    else:
                        print('Minimum amount was above usd balance.')

        else:#start selling alts
            #selling
            for i in range(len(symbols)-1): #sells everything except btc
                symbol=symbols[i+1]
                price=price_data.get_price_data('1m', symbol=symbol, exchange_str=exchange_str)
                noDecimals=np.absolute(np.log10(next(filter(lambda x:x['symbol']==symbol, exchange.fetch_markets()))['precision']['amount']))
                try:
                    balance=float(exchange.fetch_partial_balance(symbol.split('/')[0])['total'])
                except:
                    print('No balance for : ', symbol)
                current_price=price.iloc[-1]['close'].item()
                dynamic_sell_amount=round(round((-1/(50*(risk_ethbtc-1))), 2)*balance,noDecimals)
                exchange.create_limit_sell_order(symbol,dynamic_sell_amount,current_price)
                print('Sold %s of %s' %(dynamic_sell_amount, symbol))



    elif risk<0.5 and usd_balance>buy_amount:
        for i in range(len(symbols)):
            usd_balance=exchange.fetch_partial_balance('USD')['free']
            symbol=symbols[i]
            print('Symbol:', symbol)
            price=price_data.get_price_data('1m', symbol=symbol, exchange_str=exchange_str)
            noDecimals=np.absolute(np.log10(next(filter(lambda x:x['symbol']==symbol, exchange.fetch_markets()))['precision']['amount']))
            current_price=price.iloc[-1]['close'].item()
            #buy
            dynamic_buy_amount=round(buy_amount*((0.5/(risk-0.15))-1),2)
            if dynamic_buy_amount<usd_balance:
                amount_to_buy=round(dynamic_buy_amount/current_price,4)
                limit=get_limit(symbol, markets)
                if amount_to_buy>limit:
                    exchange.create_limit_buy_order(symbol,amount_to_buy,current_price)
                    print('Bought %s of %s' %(amount_to_buy, symbol))
                elif limit<usd_balance:
                    print('Amount not above limit: %s, %s' % (limit,amount_to_buy))
                    exchange.create_limit_buy_order(symbol,limit,current_price)
                    print('Bought %s of %s' %(limit, symbol))
                else:
                    print('Minimum amount was above usd balance.')
            else:
                print('No balance')
    else:
        print('Not doing anything')


#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoploss at 5% from entry INCOMPLETE

markets=ftx.fetch_markets()

price_data.update_database('BTC/USD','1d')
price=price_data.get_stored_data('BTC/USD', '1d')
weekly_data=price_data.get_price_data('1w', data=price)
fast_ema=chart.get_ema(price,50)
slow=chart.get_sma(weekly_data,50)
risk=chart.risk_indicator(fast_ema,slow).iloc[-1]['value'].item()
print('BTC risk level: ', risk)
price_data.update_database('ETH/USD','1d')
price_data.update_database('ETH/BTC','1d')
ethbtc=price_data.get_stored_data('ETH/BTC','1d')
ethbtc_weekly=price_data.get_price_data('1w', data=ethbtc) 
slow_ethbtc=chart.get_sma(ethbtc_weekly,15)
risk_ethbtc=chart.risk_indicator(ethbtc,slow_ethbtc).iloc[-1]['value'].item()
print('ETH/BTC risk level: ', risk_ethbtc)

for key, user in users.items():
    print(key)
    weekly=user['weekly']
    number_of_cryptos = 0
    run = True
    if weekly:
        buy_amount=user['daily_buy_amount']*7
        if datetime.today().weekday() != 0:
            run=False
    else:
        buy_amount=user['daily_buy_amount']
    if run:
        for name, details in user['exchanges'].items():
            print(name)
            exchange: ccxt.Exchange
            if name=='ftx':
                exchange = ccxt.ftx(details['api'])
                if 'header' in details:
                    exchange.headers = details['header']
            elif name=='cex':
                exchange = ccxt.cex(details['api'])
            symbols=details['symbols']
            number_of_cryptos = number_of_cryptos + len(symbols) 
            accumulate(risk,risk_ethbtc,name,exchange,symbols, buy_amount/number_of_cryptos) # not exactly going to be correct for my account (two exchanges)
    else:
        print('Not running today')



