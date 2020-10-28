
import enum
import user
import time
import statistics
from binance import exceptions
from datetime import datetime

account = user.User()
client = account.client

#client = Client('uuMkEps4tMUnkj0IJpDkzJRilyzylb0ajLpvQC1a9aad5X9hKSOcNLcRkXbNPcKE', 'VBmJ8JBeLglFIO3eT83lwKsAdI0PowjUf95EAlUoKiKbMf9aIQW6eO0CexXEq6su')
# client.API_URL = 'https://testnet.binance.vision/api' 
# testnet url

# from binance.websockets import BinanceSocketManager
# from twisted.internet import reactor

class TradeStatus:
   def __init__(self,sl,tp,nt):
       pass
        # self.stop_loss
        # self.take_profit
        # self.next_target

class Trade:
    def __init__(self,side,percent_amount,symbol,entry,sl,tp_array, leverage):        
        
        now = datetime.now()
        self.entry = entry #entry price
        self.symbol = str(symbol)
        self.entry_id = self.symbol+"entry"+now.strftime("%d%m%Y_%H%M%S")
        self.sl_id = self.symbol+"stoploss"+now.strftime("%d%m%Y_%H%M%S")
        self.side = str(side)

        if self.side == 'BUY':
            self.sl_side = 'SELL'
        else:
            self.sl_side = 'BUY'

        self.sl = sl
        self.tp = tp_array
        self.lev = leverage

        self.set_leverage()
        
        precision = list(filter(lambda x : x['symbol'] == self.symbol,client.futures_exchange_info()['symbols']))[0]['quantityPrecision']
        self.amount = float( "{:.{prec}f}".format( (percent_amount*account.futures_account.usdt_balance*leverage)/entry, prec=precision ))
        self.sl_callback_rate = round(abs(100*(1-(self.sl/self.entry))),1)
        
        # self.entered = self.entry_filled_check()
        # self.structure_active = self.is_structure_active()
        # self.ended = self.is_trade_over()
    
    def create_entry_order(self):
        current_price = float(list(filter(lambda x : x['symbol'] == self.symbol, user.client.get_all_tickers()))[0]['price'])
        if self.side == 'BUY':
            if current_price >= self.entry:
                entry_order = client.futures_create_order(
                    newClientOrderId = self.entry_id,
                    symbol = self.symbol,
                    side = self.side,
                    type = 'LIMIT',
                    quantity = self.amount,
                    price = self.entry,
                    timeInForce = 'GTC',
                )
            else: 
                entry_order = client.futures_create_order(
                    newClientOrderId = self.entry_id,
                    symbol = self.symbol,
                    side = self.side,
                    type = 'STOP',
                    quantity = self.amount,
                    price = self.entry,
                    stopPrice = self.entry,
                    timeInForce = 'GTC',
                )
        elif self.side == 'SELL':
            if current_price <= self.entry:
                entry_order = client.futures_create_order(
                    newClientOrderId = self.entry_id,
                    symbol = self.symbol,
                    side = self.side,
                    type = 'LIMIT',
                    quantity = self.amount,
                    price = self.entry,
                    timeInForce = 'GTC',
                )
            else: 
                entry_order = client.futures_create_order(
                    newClientOrderId = self.entry_id,
                    symbol = self.symbol,
                    side = self.side,
                    type = 'STOP',
                    quantity = self.amount,
                    price = self.entry,
                    stopPrice = self.entry,
                    timeInForce = 'GTC',
                )
    
    def create_sl(self):
        sl_trail = client.futures_create_order(
            newClientOrderId = self.sl_id,
            symbol = self.symbol,
            side = self.sl_side,
            type = 'TRAILING_STOP_MARKET',
            quantity = self.amount,
            activationPrice = self.entry,
            reduceOnly = "true",
            callbackRate = self.sl_callback_rate
        )

    def set_leverage(self):
        try:
            margin = client.futures_change_margin_type(symbol=self.symbol, marginType='ISOLATED')
            print("All good. Margin sorted.")
        except exceptions.BinanceAPIException:
            print("All good. Margin sorted.")

        leverage = client.futures_change_leverage(
            symbol = self.symbol,
            leverage = self.lev
        )

class QuickTrade(Trade) :
    def __init__(self,side,percent_amount,symbol,entry,sl,tp_array, leverage):
        super().__init__(side,percent_amount,symbol,entry,sl,tp_array, leverage)
        if len(tp_array) == 1:
            self.callback_rate = 1.6
        else:
            self.callback_rate = self.calculate_callback()
        
    def setup_trade(self):
        self.create_entry_order()
        self.set_trailing_stop()
        try:
            self.create_sl()
            print(f'Trailing SL set at {self.sl_callback_rate} from entry.')
        except exceptions.BinanceAPIException as e:
            print('Could not set SL')
            print(e)

    def set_trailing_stop(self):
        take_profit_trail = client.futures_create_order(
            symbol = self.symbol,
            side = self.sl_side,
            type = 'TRAILING_STOP_MARKET',
            quantity = self.amount,
            activationPrice = self.tp[1],
            reduceOnly = "true",
            callbackRate = self.callback_rate
        )
    
    def calculate_callback(self):
        percentage_differences = []
        n = len(self.tp)
        for i in range(1,n):
            diff = 1-(self.tp[i-1]/self.tp[i])
            percentage_differences.append(diff*100)
        return abs(round(statistics.mean(percentage_differences),1))
    
    
# class DetailedTrade(Trade): 
#     def __init__(self, price = None):
#         self.current_price = price 
        
#         #check entry order to see if its filled or not
#         self.entered = self.entry_filled_check()
#         self.structure_active = self.is_structure_active()
#         self.ended = self.is_trade_over()
        
        
        
#         account = user.User()
        
#         if (not(self.ended)): #if the trade is not invalid

#             if (not(self.entered)): #entry not created yet
#                 self.quantity = account.futures_account.trade_amount * self.entry
#                 self.create_entry_order()
#             elif (self.current_price>tp[0]): 
#                 pass
#     def get_status(self):
#         price_points = []
#         price_points.append(self.sl)
#         price_points.append(self.entry)
#         price_points.extend(self.tp)

#     def is_structure_active(self):
#         if (self.current_price is not None):
#             if (self.current_price>self.sl):
#                 return True
#             else:
#                 return False
        

#     def is_trade_over(self):
#         if (self.structure_active and self.current_price<self.sl):
#             return True
#         else:
#             return False

#     def entry_filled_check(self):
#         entry_order = user.Order(client.get_order(symbol = self.symbol, order = self.entry_id))
#         if (entry_order.status == "FILLED"):
#             return True
#         else:
#             return False

#     def set__tp(self):
#         return None
#     def set_sl(self):
#         if (self.entered):
#             pass
#         return None

# def readPrice(msg):
#     ''' define how to process incoming WebSocket messages '''

#     if 'e' in msg: #msg['e'] == 'error':
#         print(msg)
#         #reconnect
#     else:
#         for stream in msg:
#             if (stream['stream'] == tradingPair):
#                 print(stream)
#         # price['last'] = msg['c']
#         # if entry < float(price['last']):
#         #     print('buy')
#         #     trade['pair'] = tradingPair
#         #     trade['entered'] = True
#         #     tradeActive(trade) 



# bsm = BinanceSocketManager(client, user_timeout = 20)
# trading_pairs = 
# conn_key = bsm.start_multiplex_socket(['ethusdt@miniTicker','btcusdt@miniTicker','xrpusdt@miniticker'],readPrice)
# bsm.start()
