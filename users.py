from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})
client = Client(transport=transport, fetch_schema_from_transport=True)

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
    result = client.execute(query,variable_values={"name": name})
    account = result['accounts'][0]
    return {'apiKey': account['api_key'], 'secret': account['secret'], 'password': account['trading_password']}