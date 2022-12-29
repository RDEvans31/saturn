import pandas as pd
import numpy as np
import price_data as price
import ccxt
import chart
from datetime import datetime
from users import *

acc: User = getUserDetails('rob_kucoin')

kucoin_main = ccxt.kucoinfutures(acc.toApiInputObject())

symbol_binance = 'ETH/USDT'
symbol_kucoin_futures = 'ETH/USDT:USDT'

# should give me the ETH/USDT trade id
result = acc.getActiveTradesWithSymbol(symbol_kucoin_futures)
trade_id = result['id'] if result != None else None

def close_trade(trade_id, current_price):
    query = gql(
        """
        mutation CloseTrade($id: uuid!, $exit: numeric) {
          update_trades(where: {id: {_eq: $id}}, _set: {exit: $exit}) {
            affected_rows
          }
        }
      """
    )
    result = client.execute(query, variable_values={"id": trade_id, "exit": current_price})
    print(result)


class Position:
    def __init__(self, symbol, side, size, pnl, entry):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.pnl = pnl
        self.entry = entry

    def toObject(self):
        return {
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'pnl': self.pnl,
            'entry': self.entry
        }


def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)


def get_free_balance():
    return float(kucoin_main.fetch_balance()['USDT']['free'])


def get_total_balance():
    return float(kucoin_main.fetch_balance()['USDT']['total'])


def buy(amount: float, price=None):
    if price == None:
        return kucoin_main.create_order(symbol_kucoin_futures, 'market', 'buy', amount=amount, params={'leverage': 2})
    else:
        return kucoin_main.create_order(symbol_kucoin_futures, 'limit', 'buy', amount=amount, price=price, params={'leverage': 2})


def sell(amount: float, price=None):
    if price == None:
        return kucoin_main.create_order(symbol_kucoin_futures, 'market', 'sell', amount=amount, params={'leverage': 2})
    else:
        return kucoin_main.create_order(symbol_kucoin_futures, 'limit', 'sell', amount=amount, price=price, params={'leverage': 2})


def get_position():
    positions = kucoin_main.fetch_positions()
    if len(positions) == 0:
        return None
    else:
        position = next(
            filter(lambda x: x['symbol'] == symbol_kucoin_futures, kucoin_main.fetch_positions()))
        # amount is the number of contracts
        size = position['contracts']
        side = position['side']
        pnl = position['info']['unrealisedPnl'] + \
            position['info']['realisedPnl']
        entry = position['entryPrice']
        return Position(symbol_kucoin_futures, side, float(size), float(pnl), float(entry))


position = get_position()

daily = price.get_price_data('1d', symbol='ETH/USD')
current_price = daily.iloc[-1]['close'].item()
contract_size = kucoin_main.load_markets(
)[symbol_kucoin_futures]['contractSize']
trend = chart.identify_trend(daily, 7)

active_trade = position != None
output_string = ''
if active_trade:
    state = position.side
else:
    state = 'neutral'

if trend == 'uptrend' and state != 'long':

    output_string = 'flip long @ ' + \
        str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state == 'short':  # close position
        kucoin_main.cancel_all_orders()
        close_trade(trade_id, current_price)
        trade_id = None
        buy(position.size)

    trade_capital = get_free_balance()

    position_size = round((trade_capital/current_price)/contract_size)

    buy(position_size)
    state = 'long'
    entry = current_price

elif trend == 'downtrend' and state != 'short':
    output_string = 'flip short @ ' + \
        str(current_price)+' :'+datetime.utcnow().strftime("%m/%d/%y, %H:%M,%S")
    if state == 'long':  # close position
        kucoin_main.cancel_all_orders()
        close_trade(trade_id, current_price)
        trade_id = None
        sell(position.size)

    trade_capital = get_free_balance()

    position_size = round((trade_capital/current_price)/contract_size)

    state = 'short'
    entry = current_price

if trade_id != None:
    # currently active trade
    trade = {
        'id': trade_id,
        'entry': position.entry,
        'side': position.side,
        'symbol': symbol_kucoin_futures,
        'accountId': acc.id,
        'size': position.size,
        'profit': position.pnl,
    }
    if output_string != '':
        # new trade so close existing trade
        trade['exit'] = current_price
    trade_id = upsertTrade(trade)
    upsertTrade(trade)

if output_string != '':
    # a trade has been made
    new_trade = {
        'entry': entry,
        'side': state,
        'symbol': symbol_kucoin_futures,
        'size': position_size,
        'accountId': acc.id
    }
    upsertTrade(new_trade)

print(datetime.now())
print("Date: %s, Breakeven: %s, Current price: % s, PnL: % s" % (str(datetime.now()), str(position.entry), str(current_price), position.pnl))


