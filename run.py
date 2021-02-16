from datetime import datetime
import chart
import trader
import scipy 
import pyinputplus as pyip

from multiprocessing import Process
import asyncio

client=trader.client

# symbols=['EOS/USDT','LINK/USDT','ETH/USDT','WAVES/USDT','LTC/USDT','IOTA/USDT','OMG/USDT','ALGO/USDT','TRX/USDT','XLM/USDT','ADA/USDT','BAND/USDT','VET/USDT','1INCH/USDT','REN/USDT','YFII/USDT']
symbols=['BTC/USDT','ETH/USDT','LINK/USDT','DOT/USDT','REN/USDT','ADA/USDT']
def get_viable_trades(symbol):
        global viable_trades
        t = chart.get_viable_trades_for_symbol(symbol)
        if t != None:
                viable_trades.append(t)


def update_logs(user_object):
        user_object.log_account_balance()
        user_object.update_trade_data()

def setup_trades(trades):
        for t in trades:
                confirm=False
                symbol=t[0]
                res=t[1]
                sup=t[2]
                time_period_index=t[3]
                time_p=chart.time_periods[time_period_index]
                chart.identify_trend(symbol)
                # if time_period_index==0:
                #         print('Reversal')
                #         print(time_p)
                #         current_price = float(list(filter(lambda x : x['symbol'] == symbol, client.get_all_tickers()))[0]['price'])
                #         trade=trader.Reversal(sup,res,symbol)
                #         print('Support reversal:',trade.support_reversal.__dict__)
                #         print('Resistance reversal: ',trade.resistance_reversal.__dict__)
                # else:
                #         print('Breakout')
                #         print(time_p)
                #         trade=trader.BreakoutScalp(sup,res,symbol)
                #         print(trade.bullish_breakout.__dict__)
                #         print(trade.bearish_breakdown.__dict__)
                        
                confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
                #confirm=(trade.bullish_breakout.sl_callback_rate<=1) and (trade.bearish_breakdown.sl_callback_rate<=1)
                if confirm=='yes':
                        trade.setup_trade()
                else:
                        print('Trade cancelled. ')


# def trade():
        # tasks=[] # tasks will be a list of function calls on the symbols
        # for symbol in symbols:
        #         get_viable_trades(symbol)
                # t=asyncio.create_task(get_viable_trades(symbol))
                # tasks.append(t)
        # await asyncio.gather(*tasks)


def main():
        print("Started trade:", datetime.now().strftime("%H:%M:%S"))
        for symbol in symbols:
                print(symbol, chart.get_swing_trade(symbol), chart.get_current_price(symbol))
        # best_trade=min()
        print("Ended:", datetime.now().strftime("%H:%M:%S"))
        # return(viable_trades)

account = trader.account
viable_trades=[]
main()
# asyncio.run(main())
# setup_trades(viable_trades)
# update_logs(account)

        