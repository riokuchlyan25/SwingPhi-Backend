from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class BrokerageAccount(models.Model):
    """Model to store user's brokerage account information"""
    
    BROKERAGE_CHOICES = [
        ('webull', 'Webull'),
        ('robinhood', 'Robinhood'),
        ('ibkr', 'Interactive Brokers (IBKR)'),
        ('charles_schwab', 'Charles Schwab'),
        ('fidelity', 'Fidelity'),
        ('moomoo', 'Moomoo'),
        ('sofi', 'SoFi'),
        ('etrade', 'E-Trade'),
        ('etoro', 'eToro'),
        ('tradestation', 'TradeStation'),
        ('coinbase', 'Coinbase'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brokerage_accounts')
    brokerage_name = models.CharField(max_length=50, choices=BROKERAGE_CHOICES)
    account_id = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Account balance information
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    buying_power = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Error tracking
    last_error = models.TextField(blank=True, null=True)
    error_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'brokerage_name']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_brokerage_name_display()}"


class BrokerageToken(models.Model):
    """Model to store authentication tokens for brokerage APIs"""
    
    TOKEN_TYPES = [
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
        ('api_key', 'API Key'),
        ('secret', 'Secret Key'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='tokens')
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token_value = models.TextField()  # Encrypted in production
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['account', 'token_type']
    
    def __str__(self):
        return f"{self.account} - {self.get_token_type_display()}"


class Portfolio(models.Model):
    """Model to store portfolio positions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='portfolios')
    symbol = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    average_price = models.DecimalField(max_digits=10, decimal_places=4)
    current_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unrealized_pnl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unrealized_pnl_percent = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['account', 'symbol']
        ordering = ['-market_value']
    
    def __str__(self):
        return f"{self.account} - {self.symbol}"


class Transaction(models.Model):
    """Model to store transaction history"""
    
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # Brokerage's transaction ID
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    symbol = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.account} - {self.get_transaction_type_display()} - {self.symbol or 'Cash'}"


class BrokerageWebhook(models.Model):
    """Model to store webhook configurations for real-time updates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='webhooks')
    webhook_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.account} - {self.webhook_url}"


class BrokerageSettings(models.Model):
    """Model to store user preferences for brokerage integrations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='brokerage_settings')
    
    # Sync preferences
    auto_sync_enabled = models.BooleanField(default=True)
    sync_frequency_hours = models.IntegerField(default=24, validators=[MinValueValidator(1), MaxValueValidator(168)])
    
    # Notification preferences
    price_alerts_enabled = models.BooleanField(default=True)
    portfolio_alerts_enabled = models.BooleanField(default=True)
    transaction_notifications_enabled = models.BooleanField(default=True)
    
    # Privacy settings
    share_portfolio_data = models.BooleanField(default=False)
    share_transaction_data = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
