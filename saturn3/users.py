from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from models import Trade

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(
    url="https://saturn.hasura.app/v1/graphql",
    headers={
        "x-hasura-admin-secret": "Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62"
    },
)
client = Client(transport=transport, fetch_schema_from_transport=True)


class User:
    def __init__(self, id, name, apiKey, secret, password, starkPrivateKey=None):
        self.id: str = id
        self.name = name
        self.apiKey = apiKey
        self.secret = secret
        self.password = password
        if starkPrivateKey != None:
            self.starkPrivateKey = starkPrivateKey

    def toApiInputObject(self, dydx=False):
        if dydx:
            return {
                "key": self.apiKey,
                "secret": self.secret,
                "passphrase": self.password,
            }
        else:
            # this is for centralised exchanges
            return {
                "api_key": self.apiKey,
                "secret": self.secret,
                "password": self.password,
            }

    def getActiveTrades(self):
        # query that takes in id and returns active trades
        query = gql(
            """
            query GetActiveTrades($id: uuid!) {
              trades(where: {_and: {accountId: {_eq: $id}, exit: {_is_null: true}}}) {
                id
                symbol
                side
                size
                entry
                }
            }
          """
        )

        variables = {"id": self.id}
        result = client.execute(query, variable_values=variables)
        return result["trades"]

    def getActiveTradesWithSymbol(self, symbol):
        query = gql(
            """
            query GetActiveTrades($id: uuid!, $symbol: String!) {
              trades(where: {_and: {accountId: {_eq: $id}, exit: {_is_null: true}, symbol: {_eq: $symbol}}}) {
                id
                accountId
                symbol
                side
                size
                entry
                exit
                profit
                }
            }
          """
        )

        variables = {"id": self.id, "symbol": symbol}
        result = client.execute(query, variable_values=variables)
        return Trade(**result["trades"][0]) if len(result["trades"]) > 0 else None


def getUserDetails(name):
    query = gql(
        """
        query GetUserDetails($name: String!) {
          accounts(where: {account_name: {_eq: $name}}) {
            id
            account_name
            api_key
            secret
            trading_password
            starks {
              stark_private_key
            }
          }
        }
      """
    )
    result = client.execute(query, variable_values={"name": name})
    account = result["accounts"][0]
    starkpkey = (
        account["starks"][0]["stark_private_key"]
        if len(account["starks"]) > 0
        else None
    )
    return User(
        account["id"],
        account["account_name"],
        account["api_key"],
        account["secret"],
        account["trading_password"],
        starkpkey,
    )

def deleteTrade(id):
    mutation = gql(
        """
        mutation DeleteActiveTrade($id: uuid!) {
            delete_trades_by_pk(id: $id) {
                id
            }
        }
        """
    )
    result = client.execute(mutation, variable_values={id: id})
    return result




def upsertTrade(trade: Trade):
    trade_dict = {k: v for k, v in trade._asdict().items() if v is not None}
    query = gql(
        """
        mutation UpsertTrade($trade: trades_insert_input!) {
          insert_trades_one(object: $trade, on_conflict: {constraint: trades_pkey, update_columns: [exit, profit, entry]}) {
            id
          }
        }
      """
    )

    result = client.execute(query, variable_values={"trade": trade_dict})
    return result
