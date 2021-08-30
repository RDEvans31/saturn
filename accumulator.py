import ccxt
import price_data as price
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

def ftx_get_free_balance():
    return float(next(filter(lambda x:x['coin']=='USD', Savings.get_balances()))['free'])


main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='MeanReversion')

#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 


pairs=[
        {
            'asset' : 'XRP',
            'symbol':'XRP/USD',
        },
        {
            'asset' : 'ETH',
            'symbol':'ETH/USD',
        },
]

price.update_database('BTC/USD','1d')
btc_price=price.get_stored_data('BTC/USD', '1d')
weekly_data=price.get_price_data('1w', data=btc_price)
fast_ema=chart.get_ema(btc_price,50)
slow=chart.get_sma(weekly_data,50)
btc_risk=chart.risk_indicator(fast_ema,slow).iloc[-1]['value'].item()
print(btc_risk)
buy_amount=100
daily_buy_amount=buy_amount/7

if btc_risk>=0.5:
    pass
    if btc_risk>=0.9:
        pass
        #sell everythin
    #start selling
    
else:
    #buy
    current_price=btc_price.iloc[-1]['close'].item()
    dynamic_buy_amount=round(daily_buy_amount*(round(0.5/btc_risk, 1)-0.5),2)
    amount_to_buy=round(dynamic_buy_amount/current_price,4)
    if amount_to_buy>0.0001:
        Savings.place_order('BTC/USD','buy',price=current_price, type='limit', size=amount_to_buy)
    print('Bought btc')




