import requests


# Replace API_KEY and API_SECRET with your API key and secret
api_key = "6372b12d3671050001314dc3"
api_secret = "a69adc2e-457d-48a8-907b-d69f8afbbf08"

# Set the API endpoint and headers
endpoint = "https://api.kucoin.com"
headers = {
    "KC-API-KEY": api_key,
    "KC-API-SECRET": api_secret,
}

# Make a request to the API to get the list of markets
response = requests.get(f"{endpoint}/v1/market/open/coins", headers=headers)

# Print the response from the API
print(response.json())
