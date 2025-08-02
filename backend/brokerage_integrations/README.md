# Brokerage Integration System

A comprehensive Django-based system for integrating with multiple brokerage platforms to sync portfolio data, transactions, and account information.

## Supported Brokerages

The system currently supports the following brokerage platforms:

- **Webull** - Username/password authentication
- **Robinhood** - Username/password authentication  
- **Charles Schwab** - API key/secret authentication
- **Interactive Brokers (IBKR)** - API key/secret authentication
- **Fidelity** - API key/secret authentication
- **Moomoo** - Username/password authentication
- **SoFi** - Username/password authentication
- **E-Trade** - API key/secret authentication
- **eToro** - Username/password authentication
- **TradeStation** - API key/secret authentication
- **Coinbase** - API key/secret authentication

## Features

### Core Functionality
- **Multi-brokerage support** - Connect multiple accounts from different brokerages
- **Secure credential storage** - Encrypted storage of API keys and tokens
- **Real-time data sync** - Sync portfolio positions, transactions, and account balances
- **Transaction history** - Track buy/sell orders, dividends, deposits, and withdrawals
- **Portfolio tracking** - Monitor positions with unrealized P&L calculations
- **Error handling** - Robust error tracking and retry mechanisms

### Advanced Features
- **Webhook support** - Real-time notifications for account changes
- **User preferences** - Customizable sync frequency and notification settings
- **Privacy controls** - Granular control over data sharing
- **Admin interface** - Comprehensive Django admin for managing integrations

## API Endpoints

### Brokerage Management

#### Get Supported Brokerages
```
GET /brokerage_integrations/brokerages/supported/
```
Returns list of supported brokerages with their configuration requirements.

#### Connect Brokerage Account
```
POST /brokerage_integrations/brokerages/connect/
```
Connect a new brokerage account.

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

#### Get User Accounts
```
GET /brokerage_integrations/brokerages/user/{user_id}/accounts/
```
Get all connected brokerage accounts for a user.

#### Sync Account
```
POST /brokerage_integrations/brokerages/accounts/{account_id}/sync/
```
Manually sync account data.

**Request Body:**
```json
{
    "force_sync": false
}
```

#### Disconnect Account
```
DELETE /brokerage_integrations/brokerages/accounts/{account_id}/disconnect/
```
Disconnect a brokerage account.

### Portfolio & Transactions

#### Get Portfolio
```
GET /brokerage_integrations/brokerages/accounts/{account_id}/portfolio/
```
Get current portfolio positions for an account.

#### Get Transactions
```
GET /brokerage_integrations/brokerages/accounts/{account_id}/transactions/
```
Get transaction history with optional filters.

**Query Parameters:**
- `start_date` - ISO format date
- `end_date` - ISO format date  
- `transaction_type` - buy, sell, dividend, deposit, withdrawal, transfer

## Database Models

### BrokerageAccount
Stores user's brokerage account information and connection status.

### BrokerageToken
Securely stores authentication tokens for each brokerage.

### Portfolio
Tracks current portfolio positions with P&L calculations.

### Transaction
Stores transaction history with detailed information.

### BrokerageWebhook
Manages webhook configurations for real-time updates.

### BrokerageSettings
User preferences for sync frequency and notifications.

## Service Architecture

### BaseBrokerageService
Abstract base class that all brokerage services inherit from. Provides:
- Standardized authentication methods
- Common data parsing utilities
- Error handling and logging
- Response formatting

### Individual Brokerage Services
Each brokerage has its own service class implementing:
- Platform-specific authentication
- API endpoint integration
- Data transformation
- Error handling

### Service Factory
Manages service creation and configuration:
- Dynamic service instantiation
- Configuration validation
- Supported platform tracking

## Security Features

### Credential Storage
- Encrypted token storage (production)
- Secure API key management
- Token expiration handling
- Automatic token refresh

### Data Privacy
- User-controlled data sharing
- Granular privacy settings
- Secure API communication
- Audit trail logging

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations brokerage_integrations
python manage.py migrate
```

### 3. Configure Environment Variables
```bash
# Add to your .env file
BROKERAGE_ENCRYPTION_KEY=your_encryption_key_here
```

### 4. Register in Django Settings
The app is already added to `INSTALLED_APPS` in settings.py.

## Usage Examples

### Connecting a Webull Account
```python
from brokerage_integrations.services.service_factory import BrokerageServiceFactory

# Create service
service = BrokerageServiceFactory.create_service(
    'webull',
    username='user@example.com',
    password='password123'
)

# Test connection
if service.authenticate():
    # Get account info
    account_info = service.get_account_info()
    portfolio = service.get_portfolio()
    balance = service.get_balance()
```

### Syncing Account Data
```python
# Via API
POST /brokerage_integrations/brokerages/accounts/{account_id}/sync/

# Via Django ORM
account = BrokerageAccount.objects.get(id=account_id)
# Sync logic is handled in the view
```

## Error Handling

The system includes comprehensive error handling:

- **Authentication failures** - Automatic retry with token refresh
- **API rate limits** - Exponential backoff and retry logic
- **Network errors** - Connection timeout handling
- **Data validation** - Input sanitization and validation
- **Error tracking** - Detailed error logging and monitoring

## Monitoring & Logging

### Log Levels
- **INFO** - Normal operations and successful syncs
- **WARNING** - Authentication issues and retries
- **ERROR** - Failed operations and system errors
- **DEBUG** - Detailed API communication logs

### Metrics Tracked
- Sync frequency and success rates
- Authentication failure rates
- API response times
- Error counts per account
- Data freshness indicators

## Future Enhancements

### Planned Features
- **Real-time streaming** - WebSocket connections for live data
- **Advanced analytics** - Portfolio performance analysis
- **Automated trading** - Order placement and management
- **Multi-currency support** - International brokerage integration
- **Mobile app support** - Push notifications and mobile sync

### Additional Brokerages
- TD Ameritrade
- Ally Invest
- Merrill Edge
- Vanguard
- Tastyworks
- Alpaca
- Tradier

## Contributing

### Adding New Brokerages
1. Create service class inheriting from `BaseBrokerageService`
2. Implement required abstract methods
3. Add to `BrokerageServiceFactory._services`
4. Update configuration in `get_service_config()`
5. Add tests and documentation

### Testing
```bash
python manage.py test brokerage_integrations
```

## Support

For issues and questions:
- Check the Django admin interface for account status
- Review error logs for detailed information
- Test individual brokerage connections
- Verify API credentials and permissions

## License

This project is part of the Swing Phi Internship backend system. 