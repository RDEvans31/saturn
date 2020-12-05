import chart
import trader
import pyinputplus as pyip

viable_trade=chart.get_viable_trades()
for t in viable_trade:
        symbol=t[0]
        res=t[1]
        sup=t[2]
        trade=trader.BreakoutScalp(sup,res,symbol)
        print(trade.bullish_breakout.__dict__)
        print(trade.bearish_breakdown.__dict__)
        confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
        if confirm == 'yes':
                trade.setup_trade()
        else:
                print('Trade cancelled. ')