from binance.client import Client
import json
import time
import pandas as pd
from datetime import date
from binance import exceptions
#connected to actual binance account

client = Client('HrivcVPczKOE6eayp8qFVlLTBPZiaQwcGEKwfE1NhS9cRayfGDKY4n9deCloBYFK', '4VeFwan8dla9tUdMlg2G0SThcQi9g6XHLg0X6awPnTnG7Sr4ekADGdg8bN24jmE4') 
#client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
# client.API_URL = 'https://testnet.binance.vision/api' 

def filter_by_symbol(symbol,orders):
    return list(filter(lambda x: x['symbol']==symbol,orders))



def update_record(i,records,current_record,profit):
    new_record=current_record.copy()
    new_record.update({'net_profit':profit})
    new_records=records.copy()
    new_records.iloc[i]=new_record
    new_records.to_csv('~/Documents/Python Programs/saturn/trade_data.csv',index=False)
    trade_data=pd.DataFrame(pd.read_csv('~/Documents/Python Programs/saturn/trade_data.csv'))
    return(trade_data[['tradeID','entry_id','sl_id','tp1_id','tp2_id','side','symbol','entry_price','stoploss','tp1','tp2','net_profit','percentage_profit']])

class User:
    def __init__(self):
        self.client = client
        self.spot_account=SpotAccount()
        self.futures_account = FuturesAccount(self.client)

    def show(self):
        self.futures_account.show() 
    
    def log_account_balance(self):
        last_date=-1
        current_date=date.today().strftime("%d/%m/%Y")
        account_balance=self.futures_account.usdt_balance
        try:
            log=pd.DataFrame(pd.read_csv('~/Documents/Python Programs/saturn/account_balance.csv'))
            last_date=log['Date'][len(log['Date'])-1]
            last_balance=log['Balance'][len(log['Balance'])-1]
        except:
            log=pd.DataFrame(columns=['Date','Balance'])

        if (len(log['Date']) !=0 and last_date != current_date) or last_balance != account_balance:
            print('Updating')
            new_entry=pd.DataFrame([[current_date,account_balance]],columns=['Date','Balance'])
            log=log.append(new_entry,ignore_index=True)
            log.to_csv('~/Documents/Python Programs/saturn/account_balance.csv',index=False)
        
        print('Account balance:', log['Balance'][len(log['Balance'])-1])
    
    def update_trade_data(self):
        trade_data=pd.DataFrame(pd.read_csv('~/Documents/Python Programs/saturn/trade_data.csv'))
        records=trade_data[['tradeID','entry_id','sl_id','tp1_id','tp2_id','side','symbol','entry_price','stoploss','tp1','tp2','net_profit','percentage_profit']]
        for i in range(0,len(records)):
            current_record=records.iloc[i]
            entered=False
            cancelled=False
            sl_hit=False
            tp_hit=False
            #check if current record['net_profit'] is empty
            if (pd.isnull(current_record['net_profit'])):
                symbol=current_record['symbol']
                entry_id=current_record['entry_id']
                sl_id=current_record['sl_id']
                tp1_id=current_record['tp1_id']
                if (pd.isnull(current_record['tp2_id'])):
                    tp2_id=current_record['tp2_id']
                else:
                    tp2_id=None
                
                entry_order=client.futures_get_order(symbol=symbol,origClientOrderId=entry_id)
                entry_status=entry_order['status']
                
                if entry_status=='FILLED':
                    entered=True
                elif entry_status=='CANCELED' or entry_status=='EXPIRED':
                    cancelled=True

                if entered:
                    try:
                        sl_order=client.futures_get_order(symbol=symbol,origClientOrderId=sl_id)
                        sl_hit=sl_order['status']=='FILLED'
                    except:
                        pass
                    try:
                        tp1_order=client.futures_get_order(symbol=symbol,origClientOrderId=tp1_id)
                        tp_hit=tp1_order['status']=='FILLED'
                    except:
                        pass

                    if sl_hit or tp_hit:
                        if sl_hit:
                            price=float(sl_order['avgPrice'])
                            quantity=float(sl_order['executedQty'])
                            #cancel tp order
                            print("Cancelling tp: ", tp1_id)
                            try:
                                client.futures_cancel_order(symbol=symbol,origClientOrderId =tp1_id)
                            except:
                                pass
                        elif tp_hit:
                            price=float(tp1_order['avgPrice'])
                            quantity=float(tp1_order['executedQty'])
                            print("Cancelling sl: ",sl_id)
                            try:
                                client.futures_cancel_order(symbol=symbol,origClientOrderId =sl_id)
                            except:
                                pass
                        #cancel all open orders for symbol
                        open_orders=list(map(lambda x: x['clientOrderId'],filter_by_symbol(symbol,client.futures_get_open_orders())))
                        try:
                            for order in open_orders:
                                cancelled_order=client.futures_cancel_order(symbol=symbol,origClientOrderId=order)
                                print(order+" cancelled.")
                        except:
                            print("Could not cancel")

                        profit=price*quantity-current_record['entry_price']*quantity

                        if current_record['side']=='SELL':
                            profit=-1*profit

                        print(symbol)
                        print(profit)

                        update_record(i,records,current_record,profit)
                  
                if cancelled:
                    records=update_record(i,records,current_record,'Cancelled')
                
class SpotAccount():
    def  __init__(self):
        self.balances=list(filter(lambda x: float(x['free'])!=0,client.get_account()['balances']))
        self.cash_balance=float(client.get_asset_balance('USDT')['free'])
        self.estimated_total_value=self.estimate_total_value()    

    def estimate_total_value(self):
        total=self.cash_balance
        for x in self.balances:
            if x['asset']!='USDT':
                total=total+float(x['free'])*float(list(filter(lambda ticker : ticker['symbol'] == x['asset']+'USDT', client.get_all_tickers()))[0]['price'])
        return total

class FuturesAccount: 
    def __init__(self,client):

        open_orders = []
        futures_open_positions=[]

        futures_open_positions_unfiltered = self.get_futures_positions(client.futures_position_information())
        open_orders_unfiltered = list(filter(lambda x: x['status']=="NEW" or x['status']=="FILLED",client.futures_get_all_orders(limit = 10)))
        
        for position in futures_open_positions_unfiltered:
            pos_object = Position(position)
            futures_open_positions.append(pos_object)

        for order in open_orders_unfiltered:
            order_object = Order(order)
            open_orders.append(order_object)
        
        self.balance = client.futures_account_balance()
        self.usdt_balance = float(self.balance[0]['balance'])
        self.futures_open_positions = futures_open_positions
        self.open_orders = open_orders
    
    def get_futures_positions(self,position_info):
        open_positions = list(filter(lambda x: float(x['positionAmt'])!=0,position_info))
        return open_positions
        
    def show(self):
        print(self.usdt_balance)
        print(list(map(lambda x: x.__dict__, self.futures_open_positions)))
        print(list(map(lambda x: x.__dict__, self.open_orders)))
        
class Order:
    def __init__(self,orderDict):
        #print(orderDict)
        self.id = orderDict['orderId']
        self.symbol = orderDict['symbol']
        self.type = orderDict['type']
        self.price = self.getPrice(self.type,orderDict)
        self.status = orderDict['status']
        self.side = orderDict['side']
        if (self.type == 'STOP'):
            self.stopPrice = orderDict['stopPrice']
    
    def getPrice(self,orderType,orderDict):
        #print(orderDict)
        #incomplete
        switcher = {
            'MARKET': self.__averageprice(orderDict),
            'LIMIT': self.__price(orderDict),
            'STOP': self.__price(orderDict),
        }
        return switcher.get(orderType)
    
    def __averageprice(self,orderDict):
        return float(orderDict.get('avgPrice'))
    def __price(self,orderDict):
        return float(orderDict.get('price'))
class Position:
    def __init__(self,posDict):
        self.symbol = posDict['symbol']
        self.position_amount = float(posDict['positionAmt'])
        self.entry = float(posDict['entryPrice'])
        self.current_price = float(posDict['markPrice'])
        self.pnl = float(posDict['unRealizedProfit'])
        self.liq_price = float(posDict['liquidationPrice'])
        self.lev = int(posDict['leverage']) 

account=User()

# account.show()
# for x in range(1,5):
#     print("Updating")
#     time.sleep(2)
#     account = User(client)
#     print(account.futures_open_positions)

