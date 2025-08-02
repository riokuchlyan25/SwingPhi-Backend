# Brokerage Integration API Documentation

## Overview

The Brokerage Integration API provides a comprehensive interface for connecting and managing multiple brokerage accounts. The system supports 11 major brokerage platforms and provides unified access to portfolio data, transactions, and account information.

## Base URL

```
https://your-domain.com/brokerage_integrations/
```

## Authentication

Most endpoints require user authentication. Include user credentials in the request headers or body as appropriate.

## API Endpoints

### 1. Get Supported Brokerages

**Endpoint:** `GET /brokerages/supported/`

**Description:** Returns a list of all supported brokerage platforms with their configuration requirements.

**Response:**
```json
{
    "success": true,
    "brokerages": [
        "webull",
        "robinhood", 
        "charles_schwab",
        "fidelity",
        "ibkr",
        "moomoo",
        "sofi",
        "etrade",
        "etoro",
        "tradestation",
        "coinbase"
    ],
    "configurations": {
        "webull": {
            "required_fields": ["username", "password"],
            "optional_fields": ["access_token", "refresh_token"],
            "auth_method": "username_password",
            "api_documentation": "https://webull.com/api"
        },
        "charles_schwab": {
            "required_fields": ["api_key", "secret_key"],
            "optional_fields": ["access_token"],
            "auth_method": "api_key_secret",
            "api_documentation": "https://schwab.com/api"
        }
    }
}
```

### 2. Connect Brokerage Account

**Endpoint:** `POST /brokerages/connect/`

**Description:** Connect a new brokerage account to the system.

**Request Body:**
```json
{
    "user_id": 123,
    "brokerage_name": "webull",
    "credentials": {
        "username": "user@example.com",
        "password": "password123",
        "account_id": "optional_account_id"
    }
}
```

**Response:**
```json
{
    "success": true,
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Successfully connected webull account"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Authentication failed. Please check your credentials."
}
```

### 3. Get User Accounts

**Endpoint:** `GET /brokerages/user/{user_id}/accounts/`

**Description:** Get all connected brokerage accounts for a specific user.

**Response:**
```json
{
    "success": true,
    "accounts": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "brokerage_name": "webull",
            "account_id": "WB123456",
            "account_name": "My Webull Account",
            "status": "connected",
            "created_at": "2024-01-15T10:30:00Z",
            "last_sync": "2024-01-15T14:30:00Z",
            "cash_balance": 1000.00,
            "total_value": 5000.00,
            "buying_power": 2000.00
        }
    ]
}
```

### 4. Sync Account

**Endpoint:** `POST /brokerages/accounts/{account_id}/sync/`

**Description:** Manually sync account data including portfolio positions and transactions.

**Request Body:**
```json
{
    "force_sync": false
}
```

**Response:**
```json
{
    "success": true,
    "message": "Account synced successfully",
    "portfolio_count": 5,
    "transactions_count": 12
}
```

### 5. Get Portfolio

**Endpoint:** `GET /brokerages/accounts/{account_id}/portfolio/`

**Description:** Get current portfolio positions for a specific account.

**Response:**
```json
{
    "success": true,
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "brokerage_name": "webull",
    "portfolio": [
        {
            "symbol": "AAPL",
            "quantity": 10.0,
            "average_price": 150.00,
            "current_price": 160.00,
            "market_value": 1600.00,
            "unrealized_pnl": 100.00,
            "unrealized_pnl_percent": 6.67,
            "last_updated": "2024-01-15T14:30:00Z"
        },
        {
            "symbol": "GOOGL",
            "quantity": 5.0,
            "average_price": 2000.00,
            "current_price": 2100.00,
            "market_value": 10500.00,
            "unrealized_pnl": 500.00,
            "unrealized_pnl_percent": 5.00,
            "last_updated": "2024-01-15T14:30:00Z"
        }
    ]
}
```

### 6. Get Transactions

**Endpoint:** `GET /brokerages/accounts/{account_id}/transactions/`

**Description:** Get transaction history with optional filtering.

**Query Parameters:**
- `start_date` (optional): ISO format date (e.g., "2024-01-01")
- `end_date` (optional): ISO format date (e.g., "2024-01-31")
- `transaction_type` (optional): buy, sell, dividend, deposit, withdrawal, transfer

**Example Request:**
```
GET /brokerages/accounts/550e8400-e29b-41d4-a716-446655440000/transactions/?start_date=2024-01-01&transaction_type=buy
```

**Response:**
```json
{
    "success": true,
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "brokerage_name": "webull",
    "transactions": [
        {
            "transaction_id": "TXN123456",
            "transaction_type": "buy",
            "symbol": "AAPL",
            "quantity": 5.0,
            "price": 150.00,
            "amount": 750.00,
            "fees": 1.00,
            "transaction_date": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-15T10:35:00Z"
        },
        {
            "transaction_id": "TXN123457",
            "transaction_type": "dividend",
            "symbol": "AAPL",
            "quantity": null,
            "price": null,
            "amount": 25.00,
            "fees": 0.00,
            "transaction_date": "2024-01-10T09:00:00Z",
            "created_at": "2024-01-10T09:05:00Z"
        }
    ]
}
```

### 7. Disconnect Account

**Endpoint:** `DELETE /brokerages/accounts/{account_id}/disconnect/`

**Description:** Disconnect a brokerage account and remove all associated data.

**Response:**
```json
{
    "success": true,
    "message": "Successfully disconnected webull account"
}
```

## Data Models

### BrokerageAccount
```json
{
    "id": "UUID",
    "user": "User ID",
    "brokerage_name": "webull|robinhood|charles_schwab|...",
    "account_id": "Brokerage account ID",
    "account_name": "Account display name",
    "status": "pending|connected|disconnected|error",
    "is_active": true,
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "last_sync": "ISO datetime",
    "cash_balance": "Decimal",
    "total_value": "Decimal",
    "buying_power": "Decimal",
    "last_error": "Error message",
    "error_count": "Integer"
}
```

### Portfolio Position
```json
{
    "symbol": "Stock symbol",
    "quantity": "Number of shares",
    "average_price": "Average purchase price",
    "current_price": "Current market price",
    "market_value": "Total market value",
    "unrealized_pnl": "Unrealized profit/loss",
    "unrealized_pnl_percent": "Unrealized P&L percentage",
    "last_updated": "ISO datetime"
}
```

### Transaction
```json
{
    "transaction_id": "Brokerage transaction ID",
    "transaction_type": "buy|sell|dividend|deposit|withdrawal|transfer",
    "symbol": "Stock symbol (if applicable)",
    "quantity": "Number of shares (if applicable)",
    "price": "Price per share (if applicable)",
    "amount": "Total transaction amount",
    "fees": "Transaction fees",
    "transaction_date": "ISO datetime",
    "created_at": "ISO datetime"
}
```

## Error Handling

### Standard Error Response
```json
{
    "success": false,
    "error": "Detailed error message"
}
```

### Common Error Codes
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication failed)
- `404` - Not Found (account not found)
- `500` - Internal Server Error

### Error Examples

**Authentication Failed:**
```json
{
    "success": false,
    "error": "Authentication failed. Please check your credentials."
}
```

**Account Not Found:**
```json
{
    "success": false,
    "error": "Account not found"
}
```

**Unsupported Brokerage:**
```json
{
    "success": false,
    "error": "Brokerage unsupported_brokerage is not supported"
}
```

## Rate Limiting

- **Sync Operations:** Maximum 1 sync per hour per account (unless forced)
- **API Requests:** 100 requests per minute per user
- **Authentication:** 5 failed attempts per hour per account

## Security Considerations

### Data Encryption
- All sensitive credentials are encrypted at rest
- API tokens are stored securely with expiration handling
- Communication with brokerage APIs uses HTTPS

### Privacy Controls
- Users control data sharing preferences
- Granular privacy settings available
- Audit trail for all operations

### Best Practices
1. **Never store credentials in plain text**
2. **Use environment variables for sensitive configuration**
3. **Implement proper error handling**
4. **Validate all input data**
5. **Log security events**

## Integration Examples

### Python Example
```python
import requests
import json

# Get supported brokerages
response = requests.get('https://api.example.com/brokerage_integrations/brokerages/supported/')
brokerages = response.json()

# Connect a Webull account
connect_data = {
    "user_id": 123,
    "brokerage_name": "webull",
    "credentials": {
        "username": "user@example.com",
        "password": "password123"
    }
}

response = requests.post(
    'https://api.example.com/brokerage_integrations/brokerages/connect/',
    json=connect_data
)

if response.status_code == 200:
    account_id = response.json()['account_id']
    
    # Sync account data
    sync_response = requests.post(
        f'https://api.example.com/brokerage_integrations/brokerages/accounts/{account_id}/sync/',
        json={"force_sync": True}
    )
    
    # Get portfolio
    portfolio_response = requests.get(
        f'https://api.example.com/brokerage_integrations/brokerages/accounts/{account_id}/portfolio/'
    )
    
    portfolio = portfolio_response.json()
    print(f"Portfolio has {len(portfolio['portfolio'])} positions")
```

### JavaScript Example
```javascript
// Get user accounts
const response = await fetch('/brokerage_integrations/brokerages/user/123/accounts/');
const accounts = await response.json();

// Get transactions for an account
const transactionsResponse = await fetch(
    `/brokerage_integrations/brokerages/accounts/${accountId}/transactions/?start_date=2024-01-01`
);
const transactions = await transactionsResponse.json();

// Display transaction data
transactions.transactions.forEach(txn => {
    console.log(`${txn.transaction_type}: ${txn.symbol} - $${txn.amount}`);
});
```

## Webhook Support

The system supports webhooks for real-time updates:

### Webhook Configuration
```json
{
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "webhook_url": "https://your-app.com/webhooks/brokerage",
    "is_active": true
}
```

### Webhook Payload
```json
{
    "event_type": "portfolio_update|transaction|balance_change",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "brokerage_name": "webull",
    "data": {
        // Event-specific data
    },
    "timestamp": "2024-01-15T14:30:00Z"
}
```

## Monitoring & Analytics

### Key Metrics
- **Sync Success Rate:** Percentage of successful syncs
- **Authentication Failures:** Failed login attempts
- **API Response Times:** Average response time per brokerage
- **Error Rates:** Error frequency by account and brokerage
- **Data Freshness:** Time since last successful sync

### Health Checks
- **Account Status:** Monitor connection health
- **Token Expiration:** Track token refresh needs
- **Error Tracking:** Monitor and alert on failures
- **Performance Metrics:** Track API performance

## Support & Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify credentials are correct
   - Check if 2FA is enabled
   - Ensure account is not locked

2. **Sync Failures**
   - Check account status
   - Verify API permissions
   - Review error logs

3. **Data Inconsistencies**
   - Force sync to refresh data
   - Check for API changes
   - Verify account permissions

### Debug Information
- All API responses include timestamps
- Error responses include detailed messages
- Logs include request/response data
- Admin interface shows account status

### Getting Help
- Check the Django admin interface
- Review error logs for details
- Test individual brokerage connections
- Verify API credentials and permissions 