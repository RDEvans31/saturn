import time
import pandas as pd
from users import getUserDetails, upsertTrade
from dydx_helper import DydxPrivate
import chart
from models import Position, Trade, Order


class SaturnTrader:
    def __init__(self, user_name: str):  # user_name is also eth_address

        user = getUserDetails(user_name)
        userDydx = DydxPrivate(
            user_name, user.toApiInputObject(dydx=True), user.starkPrivateKey
        )
        self.user = user
        self.trader = userDydx
        self.name = user.name
        self.tradingAmount = userDydx.get_available_balance()

    def check_current_position(self, symbol: str):
        position = self.trader.get_open_position(symbol)
        return position

    def close_position(self, position: Position):
        self.update_trade(position, close=True)
        close_order = self.trader.close_position(position.market)
        return close_order

    def execute_long(self, symbol: str, amountInUsd: float):
        buy_order = self.trader.place_buy_order(symbol, amountInUsd=amountInUsd)
        return buy_order

    def execute_short(self, symbol: str, amountInUsd: float):
        sell_order = self.trader.place_sell_order(symbol, amountInUsd=amountInUsd)
        return sell_order

    def insert_new_trade(self, market: str, side: str, size: float):
        # insert new trade in db
        trade = {
            "accountId": self.user.id,
            "symbol": market,
            "size": size,
            "side": side,
            "entry": self.trader.get_current_price(market),
        }
        return upsertTrade(Trade(**trade))

    def update_trade(self, position: Position, close=False):
        # fetch active trade from db
        active_trade = self.user.getActiveTradesWithSymbol(position.market)
        if close:
            if active_trade:
                # update trade with exit
                updated_trade = active_trade._replace(exit=self.trader.get_current_price(position.market), profit=position.unrealizedPnl)
                return upsertTrade(updated_trade)
            else:
                # insert new trade with exit
                trade = {
                    "accountId": self.user.id,
                    "symbol": position.market,
                    "side": position.side,
                    "size": position.size,
                    "entry": position.entryPrice,
                    "exit": self.trader.get_current_price(position.market),
                    "profit": position.unrealizedPnl,
                }

                return upsertTrade(Trade(**trade))
        else:
            # update trade with current unrealised pnl
            if active_trade:
                updated_trade = active_trade._replace(profit=position.unrealizedPnl)
                return upsertTrade(updated_trade)
            else:
                print("Trade does not exist in the db. Creating new record.")
                return self.insert_new_trade(position.market, position.side, position.size)

    def strategy(self, price_data: pd.DataFrame, symbol: str):
        # Check the trend
        trend = chart.identify_trend(price_data, 7, 5)
        # fetch active positions from dydx
        active_position = self.check_current_position(symbol)
        state = active_position.side if active_position else "neutral"
        # Execute strategy based on the trend
        if trend == "uptrend" and state != "LONG":
            if active_position:
                self.close_position(active_position)
            orderResponse = self.execute_long(symbol, amountInUsd=self.tradingAmount)
            order = Order(**orderResponse.data["order"])
            print(self.insert_new_trade(order.market, order.side, float(order.size)))
            
        elif trend == "downtrend" and state != "SHORT":
            if active_position:
                self.close_position(active_position)
            orderResponse = self.execute_short(symbol, amountInUsd=self.tradingAmount)
            order = Order(**orderResponse.data["order"])
            print(self.insert_new_trade(order.market, order.side, float(order.size)))
        else:
            if active_position:
                print(self.update_trade(active_position))
            else:
                print("No active position. Waiting for trend to change.")

    def run(self):
        symbol = "ETH-USD"
        timeframe = "1d"
        price_data = self.trader.get_price_data(symbol, timeframe)

        self.strategy(price_data, symbol)


if __name__ == "__main__":

    trader = SaturnTrader("0x37e21e42040E76196009a88d2D2e3327a0539E11")
    trader.run()
