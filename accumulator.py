import ccxt
import price_data
import chart
import time
import schedule
import numpy as np
from datetime import datetime
from ftx_client import FtxClient
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

cex= ccxt.cex({
    'apiKey': 'Kn1RVH1X4TbIKX2usChMkQEXf10',
    'secret': 'bkksHHNIh9LgmFi8vZCInMIEWqc',
    'enableRateLimit': True,
    })

ftx.headers = {'FTX-SUBACCOUNT':'Savings'}

def ftx_get_free_balance():
    return float(next(filter(lambda x:x['coin']=='USD', Savings.get_balances()))['free'])

def get_limit(symbol, markets):
    return float(next(filter(lambda x:x['symbol']==symbol, markets))['limits']['amount']['min'])


main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='MeanReversion')

#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 
markets=ftx.fetch_markets()

daily_buy_amount=10
symbols=['BTC/USD', 'ETH/USD', 'SOL/USD', 'MATIC/USD']
price_data.update_database('BTC/USD','1d')
price=price_data.get_stored_data('BTC/USD', '1d')
weekly_data=price_data.get_price_data('1w', data=price)
fast_ema=chart.get_ema(price,50)
slow=chart.get_sma(weekly_data,50)
risk=chart.risk_indicator(fast_ema,slow).iloc[-1]['value'].item()
print('BTC risk level: ', risk)
price_data.update_database('ETH/USD','1d')
price_data.update_database('ETH/BTC','1d')
if risk>=0.6:
    ethbtc=price_data.get_stored_data('ETH/BTC','1d')
    ethbtc_weekly=price_data.get_price_data('1w', data=ethbtc) 
    slow_ethbtc=chart.get_sma(ethbtc_weekly,15)
    risk_ethbtc=chart.risk_indicator(ethbtc,slow_ethbtc).iloc[-1]['value'].item()
    print('ETHBTC risk level', risk_ethbtc)
    #sell btc
    price=price_data.get_price_data('1m', symbol='BTC/USD')
    try:
        balance=float(ftx.fetch_partial_balance('BTC')['total'])
    except:
        print('No balance for BTC ')
    current_price=price.iloc[-1]['close'].item()
    dynamic_sell_amount=round((-1/(50*(risk-1))), 2)*balance
    Savings.place_order('BTC/USD','sell',price=current_price, type='limit', size=dynamic_sell_amount)
    print('Sold %s of %s' %(dynamic_sell_amount, 'BTC/USD'))
    usd_amount=dynamic_sell_amount*current_price
    if risk_ethbtc<0.5: #move those profits over to eth
            usd_balance=ftx.fetch_partial_balance('USD')['total']   
            eth_price=price_data.get_price_data('1m',symbol='ETH/USD')       
            #buy
            current_eth_price=eth_price.iloc[-1]['close'].item()
            buy_amount=usd_amount/current_eth_price
            if buy_amount<usd_balance:
                amount_to_buy=round(buy_amount/current_eth_price,4)
                limit=get_limit('ETH/USD', markets)
                if amount_to_buy>limit:
                    Savings.place_order('ETH/USD','buy',price=current_price, type='limit', size=amount_to_buy)
                    print('Bought %s of %s' %(amount_to_buy, 'ETH/USD'))
                else:
                    print('Amount not above limit: %s, %s' % (limit,amount_to_buy))
                    Savings.place_order('ETH/USD','buy',price=current_price, type='limit', size=limit)
                    print('Bought %s of %s' %(limit, 'ETH/USD'))

    else:#start selling alts
        #selling
        for i in range(len(symbols)-1):
            symbol=symbols[i+1]
            price=price_data.get_price_data('1m', symbol=symbol)
            try:
                balance=float(ftx.fetch_partial_balance(symbol.split('/')[0])['total'])
            except:
                print('No balance for : ', symbol)
            current_price=price.iloc[-1]['close'].item()
            dynamic_sell_amount=round((-1/(50*(risk_ethbtc-1))), 2)*balance
            Savings.place_order(symbol,'sell',price=current_price, type='limit', size=dynamic_sell_amount)
            print('Sold %s of %s' %(dynamic_sell_amount, symbol))



elif risk<0.5:
    for i in range(len(symbols)):
        usd_balance=ftx.fetch_partial_balance('USD')['total']
        symbol=symbols[i]
        price=price_data.get_price_data('1m', symbol=symbol)
        try:
            balance=float(ftx.fetch_partial_balance(symbol.split('/')[0])['total'])
        except:
            print('No balance for : ', symbol)
        current_price=price.iloc[-1]['close'].item()
            
            #buy
        dynamic_buy_amount=round(daily_buy_amount*((0.5/(risk-0.15))-1),2)
        if dynamic_buy_amount<usd_balance:
            amount_to_buy=round(dynamic_buy_amount/current_price,4)
            limit=get_limit(symbol, markets)
            if amount_to_buy>limit:
                Savings.place_order(symbol,'buy',price=current_price, type='limit', size=amount_to_buy)
                print('Bought %s of %s' %(amount_to_buy, symbol))
            else:
                print('Amount not above limit: %s, %s' % (limit,amount_to_buy))
                Savings.place_order(symbol,'buy',price=current_price, type='limit', size=limit)
                print('Bought %s of %s' %(limit, symbol))



