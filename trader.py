import user
import pandas as pd
from decimal import Decimal
from binance import exceptions
from datetime import datetime
import math
import price_data
import sys

def format_tp(tp_array,precision):
    try:
        return list(map(lambda x: float( "{:.{prec}f}".format(x, prec=precision )),tp_array))
    except:
        print(tp_array)

def format_sl(sl,precision):
    try:
        return float( "{:.{prec}f}".format(sl, prec=precision))
    except:
        print(sl)

def round_one_place_down(n):
    d=Decimal(str(n))
    no_of_decimal_places=-1*d.as_tuple().exponent
    return round(n,no_of_decimal_places-1)


class Trade:
    def __init__(self,side,tp,symbol,entry,sl):        
        
        now = datetime.now()
        self.side = str(side)
        if self.side == 'BUY':
            self.sl_side = 'SELL'
        else:
            self.sl_side = 'BUY'
        self.trade_id=self.side+"_"+symbol+"_"+now.strftime("%d%m%Y_%H%M%S")
        self.entry = entry #entry price
        self.sl=sl
        self.symbol = str(symbol)
        self.tp=tp
        self.entry_id = self.trade_id+"entry"
        self.sl_id = self.trade_id+"stoploss"
        self.tp_id = self.trade_id+"tp"     
        
        total_balance=account.futures_account.usdt_balance
        proposed_amount=0.01*(total_balance)/abs(self.entry-self.sl)
        capital_risked=round(0.1*total_balance)
        self.leverage=math.floor(proposed_amount/(capital_risked*self.entry))
        

        #should check whether there is enough free


        

        self.set_leverage()
        self.capital_risked=0.1*account.futures_account.usdt_balance
        self.trade_capital=self.capital_risked*self.leverage
        
        precision = list(filter(lambda x : x['symbol'] == self.symbol,client.futures_exchange_info()['symbols']))[0]['quantityPrecision']
        self.amount = float( "{:.{prec}f}".format( (self.trade_capital)/entry, prec=precision ))
        self.worst_case_amount=abs(self.entry*self.amount-self.sl*self.amount)

        self.entry_set=False
        self.sl_set=False
        self.tp_set=False
        
        # self.entered = self.entry_filled_check()
        # self.structure_active = self.is_structure_active()
        # self.ended = self.is_trade_over()
    
    def create_entry_order(self):
        current_price = float(list(filter(lambda x : x['symbol'] == self.symbol, user.client.get_all_tickers()))[0]['price'])
        if self.side == 'BUY':
            pass
            
        elif self.side == 'SELL':
            pass

    def set_leverage(self):
        pass
    
    def calculate_worst_case(self):
        amount_lost=float(self.worst_case_amount-self.trade_capital)
        percentage_loss=float(100*((self.worst_case_amount/self.trade_capital)-1))
        output=("Worst case: {0}%=${1}").format(percentage_loss,amount_lost)
        return output

    def update_records(self):
        td=pd.DataFrame()
        try:
            trade_data=pd.read_csv('~/Documents/Python Programs/saturn/trade_data.csv')
            td=pd.DataFrame(trade_data)
        except:
            print('Could not read file.')
            
        
        new_trade=pd.DataFrame(
            data=[[self.trade_id,self.entry_id,self.sl_id,self.tp_id,self.side,self.symbol,self.capital_risked,self.entry,self.sl,self.tp,None,None]],
            columns=['tradeID', 'entry_id', 'sl_id', 'tp_id', 'side','symbol', 'risked_capital', 'entry_price', 'stoploss', 'tp', 'net_profit', 'percentage_profit'],
            )
        td=td.append(new_trade,ignore_index=True)
        td.to_csv('~/Documents/Python Programs/saturn/trade_data.csv',index=False)
        trade_data=pd.read_csv('~/Documents/Python Programs/saturn/trade_data.csv')

    def cancel_trade(self):
        pass

