import price_data as price
import asyncio
import ccxt

ftx_ccxt = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True
})

def fetch_position(exchange: ccxt.Exchange):
    request = {
        'showAvgPrice': True,
    }
    response = exchange.privateGetPositions(ftx_ccxt.extend(request))
    result = ftx_ccxt.safe_value(response, 'result', [])
    print(next(filter(lambda x: x['future']=='ETH-PERP',result)))

    # print(ftx_ccxt.parse_position(result[i]))
    # ftx_ccxt.parse_position(result[i])

fetch_position(ftx_ccxt)