import ccxt
import price_data as price
import chart
import time
import schedule
import numpy as np
from datetime import datetime
from ftx_client import FtxClient

ftx_ccxt = ccxt.ftx({
    'apiKey': 'mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',
    'secret': 'oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',
    'enableRateLimit': True,
})

main=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B')
Savings=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='Savings')
MeanReversion=FtxClient(api_key='mFRyLR4AAhLTc5RlWov3PKTcIbMHw3vGZwiHnsrn',api_secret='oKaY1WEqTuhnNnq0iRi_Ry-CYckvE89-gPUPf21B',subaccount_name='MeanReversion')


# def append_new_line(file_name, text_to_append):
#     """Append given text as a new line at the end of file"""
#     # Open the file in append & read mode ('a+')
#     with open(file_name, "a+") as file_object:
#         # Move read cursor to the start of file.
#         file_object.seek(0)
#         # If file is not empty then append '\n'
#         data = file_object.read(100)
#         if len(data) > 0:
#             file_object.write("\n")
#         # Append text at the end of file
#         file_object.write(text_to_append)

# position=next(filter(lambda x: x['future']=='ETH-PERP',ftx_ccxt.fetch_positions()))
# position_size=float(position['size'])
# if position_size==0:
#     print('No position, starting state: neutral')
#     precision=int(abs(np.log10(float(next(filter(lambda x:x['symbol']=='ETH/USD',ftx_ccxt.fetch_markets()))['precision']['amount']))))
#     daily=price.get_price_data('1d',symbol='ETH/USD')
#     hourly=price.get_price_data('1h',symbol='ETH/USD')
#     state=chart.identify_trend(daily,hourly)
#     trade_capital=float(input("Enter trade capital= "))

# elif position['side']=='buy':
#     print('starting state: long')
#     state='long'
# elif position['side']=='sell':
#     print('starting state: short')
#     state='short'

# def new_hour():
#    return int(time.time())/3600 == int(time.time())//3600

# def check_starting_conditions():
#     global state
#     print('Checking starting conditions')
#     hourly=price.get_price_data('1h',symbol='ETH/USD')
#     if state=='neutral':
#         state=chart.identify_trend(daily,hourly) #MANUALLY CHANGE IF CURRENLT HAS OPEN POSITION
#     if (state!='neutral' and position_size==0.0):
#         print('starting conditions not met')
#     else:
#         return schedule.CancelJob



# def run():
#     global state
    # print(datetime.now())
    # daily=price.get_price_data('1d',symbol='ETH/USD')
    # hourly=price.get_price_data('1h',symbol='ETH/USD')
    # trend=chart.identify_trend(daily,hourly)
    # current_price=hourly.iloc[-1]['close']
    # usd_balance=float(list(filter(lambda x: x['coin']=='USD',ftx_ccxt.fetch_balance()['info']['result']))[0]['total'])
    # position=next(filter(lambda x: x['future']=='ETH-PERP',ftx_ccxt.fetch_positions()))
    # position_size=float(position['size'])
    # if position_size==0:
    #     position_size=trade_capital/current_price
    #     position_size=round(position_size,precision)
    #     print('new position size= ', position_size)

    # if trend == 'uptrend' and state != 'long':
        
    #     output_string='flip long @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    #     print('flip long @ '+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S"))
    #     if state=='short':#close position
    #         ftx.create_order('ETH-PERP','market','buy',position_size)
    #     ftx.create_order('ETH-PERP','market','buy',position_size)
    #     state='long'
    # elif trend == 'downtrend' and state != 'short':
    #     output_string='flip short @ '+ str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    #     print('flip short @ '+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S"))
    #     if state=='long':#close position
    #         ftx.create_order('ETH-PERP','market','sell',position_size)
    #     ftx.create_order('ETH-PERP','market','sell',position_size)
    #     state='short'

    # else:
    #     output_string=''
    #     print('no change')
    # if output_string!='':
    #     append_new_line('ETH_swingtrader_log.txt',output_string)
    # print("Current price: ",str(current_price))
    
    # time_till_next_hour=3600-time.time()%3600
    # time.sleep(time_till_next_hour-5)

# schedule.every().minute.at(":01").do(check_starting_conditions)
# while state!='neutral' and position_size==0.0:
#     schedule.run_pending()
#     #scheduled to run the job every hour
# print('starting')
# schedule.clear()
# #sleep until just before the next hour
# sleeping_time=3600-time.time()%3600 -5
# print('sleeping for ', round(sleeping_time/60))
# time.sleep(sleeping_time)
# schedule.every().hour.at("00:01").do(run)
# while True:
#     schedule.run_pending()


print(ftx_ccxt.fetch_balance())

