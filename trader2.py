import numpy as np
import pandas as pd
import ccxt
import price_data as price
import chart

ftx = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

daily=price.get_price_data('1d',symbol='ETH/USD')
hourly=price.get_price_data('1h',symbol='ETH/USD')
trend=chart.identify_trend(daily,hourly)

state='neutral'

if trend == 'uptrend':
    
elif trend == 'downtrend':
    
else:
    pass