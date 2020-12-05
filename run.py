import chart
import trader

viable_trade=chart.get_viable_trades()
for t in viable_trade:
        symbol=t[0]
        res=t[1]
        sup=t[2]
        trade=trader.BreakoutScalp(sup,res,symbol)
        confirm = pyip.inputYesNo(prompt="Confirm? yes or no: ")
        if confirm == 'yes':
                trade.setup_trade()

        else:
                print('Trade cancelled. ')