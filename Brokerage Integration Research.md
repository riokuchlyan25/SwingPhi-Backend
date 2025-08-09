## Brokerage Data APIs for Account Balances & Holdings

### Webull
- Webull offers a REST API via its Developer Portal. You must open a brokerage account, apply for API access in “OpenAPI Management,” and wait for approval. After approval you generate an App Key/Secret, then use their SDK (e.g., `webull-openapi-sdk`) to fetch account info.
- Status: Requires developer/app approval (no direct snippet here).
- Developer portal: https://developer.webull.com/

### Robinhood
- Robinhood has no public developer API. Third-party fintech apps typically use data aggregators (e.g., SnapTrade or Plaid) that let users link Robinhood via OAuth/login.
- Status: Use an aggregator; no direct public API.
- Aggregators: https://www.snaptrade.com/ • https://plaid.com/

### Interactive Brokers (IBKR)
- IBKR provides official APIs (TWS API or Client Portal API) that allow account data access. No special developer approval beyond having an IB account is required. You can connect to TWS or IB Gateway and request account summary or positions.
- Example (requires TWS/Gateway running and logged in):

```python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    def accountSummary(self, reqId, account, tag, value, currency):
        print(account, tag, value, currency)

app = IBApp()
app.connect("127.0.0.1", 7497, clientId=0)    # default TWS port
app.reqAccountSummary(1, "All", "$LEDGER:ALL")
app.run()
```

- This prints account balances (e.g., cash) and holdings. IBKR’s API lets you access real-time account/position data.
- Docs: https://www.interactivebrokers.com/en/trading/ib-api.php

### Charles Schwab
- Schwab has a Developer Portal with REST APIs for accounts and trading. You must create a Schwab Developer account and register an application, selecting the Accounts & Trading APIs. Schwab reviews the app (typically a few days) and then issues OAuth credentials. Use OAuth2 to obtain access tokens and call their endpoints.
- Status: Registration/approval required; OAuth flow.
- Developer portal: https://developer.schwab.com/

### Fidelity
- Fidelity does not offer a fully open API to external developers. Authorized fintech apps use Fidelity’s “Access” system. Users log in and authorize an app via Fidelity’s website; then that app can read balances and holdings. For example, SnapTrade provides a Fidelity integration where users grant consent.
- Status: Use an aggregator (Plaid/SnapTrade); no open API keys for general developers.
- Aggregators: https://www.snaptrade.com/ • https://plaid.com/

### Moomoo (Futu)
- Moomoo provides an OpenAPI (via Futu) for market data and trading. You download and run their OpenD gateway locally, then use the Futu SDK (Python `futu` package) to access account data. You only need your Moomoo/Futu credentials (no separate API key/approval).
- Example (using Futu SDK to fetch positions):

```python
from futu import OpenSecTradeContext, TrdMarket, RET_OK

# Connect to the local OpenD gateway (ensure OpenD is running)
trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
ret, data = trd_ctx.position_list_query()  # query all positions
if ret == RET_OK:
    print(data)  # DataFrame of holdings (code, qty, etc.)
trd_ctx.close()
```

- This uses your logged-in Moomoo account via the local OpenD service. No developer approval is required beyond having the account.
- Docs: https://openapi.futunn.com/futu-api-doc/intro/en/

### SoFi
- SoFi Invest has no public API. To access SoFi account balances, use a financial data aggregator (e.g., Plaid). Users log in to SoFi via the aggregator and grant consent.
- Status: Use an aggregator (Plaid).
- Aggregator: https://plaid.com/

### E*TRADE
- E*TRADE provides a REST API platform for account data, balances, and trading. Register for a developer account and create an app to get OAuth keys (sandbox key available immediately). After getting keys, call the REST endpoints for balances/positions.
- Status: Developer registration + OAuth; onboarding required.
- Developer: https://developer.etrade.com/

### eToro
- eToro does not provide an open API to users as of 2025. Past developer programs are discontinued. Current solutions involve third-party services (e.g., Vezgo for crypto wallets) but there’s no general public brokerage API.
- Status: No public API; consider aggregators where available.

### TradeStation
- TradeStation offers REST and FIX APIs on its Developer Portal. You can create an API key via their site. Individuals can access the Trading API for personal use. Sign up, create an app to get client key/secret, then use OAuth.
- Status: Developer signup + OAuth.
- Developer: https://developer.tradestation.com/

### Coinbase
- Coinbase’s Advanced Trade API is open to all users via its Developer Platform. Generate API key/secret in the Coinbase Developer portal, then use their REST API or official SDK to fetch account balances and holdings.
- Example (official Python SDK):

```python
from coinbase.rest import RESTClient

api_key = "YOUR_COINBASE_API_KEY"
api_secret = "YOUR_COINBASE_API_SECRET"
client = RESTClient(api_key, api_secret)
accounts = client.get_accounts()  # list of account balances
print(accounts)
```

- Docs: https://docs.cdp.coinbase.com/advanced-trade/docs/welcome

---

### Sources
Official developer sites and documentation for each broker (linked above). Each snippet demonstrates how to implement data retrieval where no prior approval is needed (all operations involve end-user consent and API keys; no password scraping).


