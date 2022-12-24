from calendar import calendar
from math import remainder
import numpy as np
import pandas as pd
from pandas.core.base import DataError
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://saturn.hasura.app/v1/graphql", headers={'x-hasura-admin-secret': 'Rc07SJt4ryC6RyNXDKFRAtFmRkGBbT8Ez3SdaEYsHQoHemCldvs52Kc803oK8X62'})
client = Client(transport=transport, fetch_schema_from_transport=True)

def getUserDetails(name):
    query = gql(
        """
        query GetUserDetails($name: String!) {
          accounts(account_name: (_eq: $name)) {
            account_name
            api_key
            secret
            id
          }
      }
    """
    )
    result = client.execute(query,={"name": name})
    print(result)
    return result
print(getUserDetails('rob_kucoin'))

