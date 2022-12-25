from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={
                             'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})
client = Client(transport=transport, fetch_schema_from_transport=True)


class User:
  def __init__(self, id, name, apiKey, secret, password):
      self.id: str = id
      self.name = name
      self.apiKey = apiKey
      self.secret = secret
      self.password = password

  def toApiInputObject(self):
      return {
          'api_key': self.apiKey,
          'secret': self.secret,
          'password': self.password,
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

      variables = {
          'id': self.id
      }
      result = client.execute(query, variable_values=variables)
      return result['trades']

  def getActiveTradesWithSymbol(self,symbol):
      query = gql(
          """
            query GetActiveTrades($id: uuid!, $symbol: String!) {
              trades(where: {_and: {accountId: {_eq: $id}, exit: {_is_null: true}, symbol: {_eq: $symbol}}}) {
                id
                symbol
                side
                size
                entry
                }
            }
          """
      )

      variables = {
          'id': self.id,
          'symbol': symbol
      }
      result = client.execute(query, variable_values=variables)
      return result['trades'][0] if len(result['trades']) > 0 else None

def getUserDetails(name):
    query = gql(
        """
        query GetUserDetails($name: String!) {
          accounts(where: {account_name: {_eq: $name}}) {
            account_name
            api_key
            secret
            trading_password
            id
          }
        }
      """
    )
    result = client.execute(query, variable_values={"name": name})
    account = result['accounts'][0]
    return User(account['id'], account['account_name'], account['api_key'], account['secret'], account['trading_password'])


def upsertTrade(trade):
    query = gql(
        """
        mutation UpsertTrade($trade: trades_insert_input!) {
          insert_trades_one(object: $trade, on_conflict: {constraint: trades_pkey, update_columns: [exit, profit]}) {
            id
          }
        }
      """
    )
    result = client.execute(query, variable_values={"trade": trade})
    return result
