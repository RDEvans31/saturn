import ccxt
from pandas.core import api
import price_data
import chart
import numpy as np
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from users import users

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
    'uid' : 'up109520414',
    'apiKey': '1X2uEcPlvBCe4CcMtzWKguG1SDI',
    'secret': '8JY4fDg6hRz0DTolZHz77XPdC1o',
    'enableRateLimit': True,
    })

def get_limit(symbol, markets):
    return float(next(filter(lambda x:x['symbol']==symbol, markets))['limits']['amount']['min'])




#1. read from list of dictonaries conatining investments.
#2. for each investment, purchase amount equivalent to money set aside
#3. update mean entry, and set stoposs at 5% from entry 

for key, user in users.items():
    daily_buy_amount=user['daily_buy_amount']
    for name, details in user['exchanges'].items():
        exchange: ccxt.Exchange
        if name=='ftx':
            exchange = ccxt.ftx(details['api'])
        elif name=='cex':
            exchange = ccxt.ftx(details['api'])
        else:
            exchange = ccxt.ftx(details['api'])
        symbols=details['symbols']


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
ethbtc=price_data.get_stored_data('ETH/BTC','1d')
ethbtc_weekly=price_data.get_price_data('1w', data=ethbtc) 
slow_ethbtc=chart.get_sma(ethbtc_weekly,15)
risk_ethbtc=chart.risk_indicator(ethbtc,slow_ethbtc).iloc[-1]['value'].item()




