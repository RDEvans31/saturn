import chart
import trader
import pyinputplus as pyip

viable_trade=chart.get_viable_trades()
time=chart.time_periods
for t in viable_trade:
        confirm=False
        symbol=t[0]
        res=t[1]
        sup=t[2]
        time_period_index=t[3]
        time_p=time[time_period_index]
        if time_period_index==0:
                print('Reversal')
                print(time_p)
                trade=trader.FalseBreakout(sup,res,symbol)
                print('Support reversal:',trade.support_reversal.__dict__)
                print('Resistance reversal: ',trade.resistance_reversal.__dict__)
        else:
                print('Breakout')
                print(time_p)
                trade=trader.BreakoutScalp(sup,res,symbol)
                print(trade.bullish_breakout.__dict__)
                print(trade.bearish_breakdown.__dict__)
                
        confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
        #confirm=(trade.bullish_breakout.sl_callback_rate<=1) and (trade.bearish_breakdown.sl_callback_rate<=1)
        if confirm=='yes':
                trade.setup_trade()
        else:
                print('Trade cancelled. ')