import datetime
from dydx3 import Client
from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.constants import ORDER_SIDE_SELL
from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import ORDER_TYPE_MARKET
from dydx3.constants import MARKET_ETH_USD
from dydx3.constants import TIME_IN_FORCE_GTT
from dydx3.constants import TIME_IN_FORCE_IOC
from dydx3.constants import POSITION_STATUS_OPEN
import time
import numpy as np
import pandas as pd
from models import Position


def convert_iso_string_to_unix_timestamp(iso_string):
    """Converts an ISO string to a Unix timestamp.

  Args:
    iso_string: The ISO string to convert.

  Returns:
    The Unix timestamp.
  """

    # Parse the ISO string into a datetime object.
    datetime_object = datetime.datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Get the Unix timestamp from the datetime object.
    unix_timestamp = datetime_object.timestamp()

    return unix_timestamp


# DydxPublic class just for public access
class DydxPublic:
    def __init__(self):
        self.client = Client(
            host="https://api.dydx.exchange", network_id=NETWORK_ID_MAINNET,
        )

    def get_candles(self, market: str, resolution="1DAY", limit=30):
        res = self.client.public.get_candles(
            market=market, resolution=resolution, limit=limit
        )
        return res.data.get("candles")

    def get_current_price(self, market):
        res = self.client.public.get_candles(
            market=market, resolution="1MIN", limit="1"
        )
        return res.data.get("candles")[0].get("close")

    def get_price_data(self, symbol, timeframe, fromDateTime=None, toDateTime=None):
        timeframes = {
            "4h": "4HOUR",
            "1d": "1DAY",
            "1h": "1HOUR",
            "1m": "1MIN",
        }

        timeframe_encoded = timeframes[timeframe]

        candles = []

        candles_retrieved = False
        max_attempts = 5
        attempts = 0
        while not (candles_retrieved) and attempts < max_attempts:
            try:
                candles = self.get_candles(symbol, timeframe_encoded, limit=100)
                candles_retrieved = True
                raise Exception("Error fetching price")
            except:
                pass

        if candles == []:
            return pd.DataFrame([])

        timestamps = list(
            map(
                lambda x: convert_iso_string_to_unix_timestamp(x.get("startedAt")),
                candles,
            )
        )
        open_price = np.array(list(map(lambda x: x["open"], candles)), dtype=float)
        highest = np.array(list(map(lambda x: x["high"], candles)), dtype=float)
        lowest = np.array(list(map(lambda x: x["low"], candles)), dtype=float)
        closes = np.array(list(map(lambda x: x["close"], candles)), dtype=float)

        df = pd.DataFrame(
            {
                "unix": timestamps,
                "close": closes,
                "high": highest,
                "low": lowest,
                "open": open_price,
            }
        ).sort_values(by=["unix"], ignore_index=True)

        return df


class DydxPrivate(DydxPublic):
    def __init__(self, ethereum_address, api_credentials, stark_private_key=None):
        def get_user(client: Client):
            user = client.private.get_user()
            return user

        def get_account(client: Client):
            account = client.private.get_account()
            return account

        self.stark_private_key = stark_private_key
        self.client = Client(
            host="https://api.dydx.exchange",
            default_ethereum_address=ethereum_address,
            network_id=NETWORK_ID_MAINNET,
            stark_private_key=stark_private_key,
            api_key_credentials=api_credentials,
        )
        self.account = get_account(self.client).data.get("account")
        self.position_id = self.account.get("positionId")
        self.user = get_user(self.client).data

    def get_available_balance(self):
        account = self.account
        return float(account.get("equity"))

    def get_current_price(self, market):
        res = self.client.public.get_candles(
            market=market, resolution="1MIN", limit="1"
        )
        return res.data.get("candles")[0].get("close")

    def get_open_position(self, market: str) -> Position | None:
        res = self.client.private.get_positions(
            market=market, status=POSITION_STATUS_OPEN, limit="1"
        )
        return (
            Position(**res.data.get("positions")[0])
            if len(res.data.get("positions")) > 0
            else None
        )

    def close_position(self, currency: str):
        # get position
        position = self.get_open_position(currency)
        if position:
            position_size = float(position.size)
            side = position.side
            if side == "LONG":
                return self.place_sell_order(
                    position.market, amountInCurrency=position_size
                )
            elif side == "SHORT":
                return self.place_buy_order(
                    position.market, amountInCurrency=position_size
                )
            else:
                raise Exception("Position side not supported")

    def place_buy_order(
        self,
        market: str,
        amountInUsd: float = 0,
        price: float = 0,
        amountInCurrency: float = 0,
    ):
        if not (amountInCurrency) and not (amountInUsd):
            raise Exception("Amount in currency or usd must be specified")

        if not (price == 0):
            orderSize = round(
                amountInCurrency if amountInCurrency else amountInUsd / float(price), 3
            )
            order = self.client.private.create_order(
                position_id=self.position_id,
                market=market,
                side=ORDER_SIDE_BUY,
                order_type=ORDER_TYPE_LIMIT,
                post_only=False,
                size=str(round(orderSize, 3)),
                price=str(price),
                limit_fee="0.015",
                expiration_epoch_seconds=time.time() + 30 * 60,
                time_in_force=TIME_IN_FORCE_GTT,
            )
            return order
        else:
            currentPrice = self.get_current_price(market)
            orderSize = round(
                amountInCurrency
                if amountInCurrency
                else amountInUsd / float(currentPrice),
                3,
            )

            order = self.client.private.create_order(
                position_id=self.position_id,
                market=market,
                side=ORDER_SIDE_BUY,
                order_type=ORDER_TYPE_MARKET,
                post_only=False,
                size=str(orderSize),
                price=str(currentPrice),
                limit_fee="0.015",
                expiration_epoch_seconds=time.time() + 30 * 60,
                time_in_force=TIME_IN_FORCE_IOC,
            )
            return order

    def place_sell_order(
        self, market, amountInUsd: float = 0, price=None, amountInCurrency: float = 0,
    ):
        if not (amountInCurrency) and not (amountInUsd):
            raise Exception("Amount in market or usd must be specified")

        if not (price == None):
            orderSize = round(
                amountInCurrency if amountInCurrency else amountInUsd / float(price), 3
            )
            order = self.client.private.create_order(
                position_id=self.position_id,
                market=market,
                side=ORDER_SIDE_SELL,
                order_type=ORDER_TYPE_LIMIT,
                post_only=False,
                size=str(orderSize),
                price=str(price),
                limit_fee="0.015",
                expiration_epoch_seconds=time.time() + 30 * 60,
                time_in_force=TIME_IN_FORCE_GTT,
            )
            return order
        else:
            currentPrice = self.get_current_price(market)
            orderSize = round(
                amountInCurrency
                if amountInCurrency
                else amountInUsd / float(currentPrice),
                3,
            )
            order = self.client.private.create_order(
                position_id=self.position_id,
                market=market,
                side=ORDER_SIDE_SELL,
                order_type=ORDER_TYPE_MARKET,
                price=str(currentPrice),
                post_only=False,
                size=str(orderSize),
                limit_fee="0.015",
                expiration_epoch_seconds=time.time() + 30 * 60,
                time_in_force=TIME_IN_FORCE_IOC,
            )
            return order

    def place_trade(self, market, price, side, leverage=1):
        availableBalance = self.get_available_balance()
        if side == "buy":
            return self.place_buy_order(market, availableBalance * leverage, price)
        elif side == "sell":
            return self.place_sell_order(market, availableBalance * leverage, price)
        else:
            raise Exception("Side not supported")
