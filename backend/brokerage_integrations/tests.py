from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from .models import (
    BrokerageAccount, BrokerageToken, Portfolio, Transaction, 
    BrokerageWebhook, BrokerageSettings
)
from .services.service_factory import BrokerageServiceFactory


class BrokerageIntegrationTestCase(TestCase):
    """Test cases for brokerage integration functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.account = BrokerageAccount.objects.create(
            user=self.user,
            brokerage_name='webull',
            account_id='TEST123',
            account_name='Test Account',
            status='connected',
            cash_balance=Decimal('1000.00'),
            total_value=Decimal('5000.00'),
            buying_power=Decimal('2000.00')
        )
        
        self.settings = BrokerageSettings.objects.create(
            user=self.user,
            auto_sync_enabled=True,
            sync_frequency_hours=24,
            price_alerts_enabled=True,
            portfolio_alerts_enabled=True
        )
    
    def test_brokerage_account_creation(self):
        """Test creating a brokerage account"""
        account = BrokerageAccount.objects.create(
            user=self.user,
            brokerage_name='robinhood',
            account_id='RH123',
            account_name='Robinhood Account',
            status='pending'
        )
        
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.brokerage_name, 'robinhood')
        self.assertEqual(account.status, 'pending')
        self.assertTrue(account.is_active)
    
    def test_portfolio_position_creation(self):
        """Test creating portfolio positions"""
        position = Portfolio.objects.create(
            account=self.account,
            symbol='AAPL',
            quantity=Decimal('10.0'),
            average_price=Decimal('150.00'),
            current_price=Decimal('160.00'),
            market_value=Decimal('1600.00'),
            unrealized_pnl=Decimal('100.00'),
            unrealized_pnl_percent=Decimal('6.67')
        )
        
        self.assertEqual(position.account, self.account)
        self.assertEqual(position.symbol, 'AAPL')
        self.assertEqual(float(position.quantity), 10.0)
        self.assertEqual(float(position.average_price), 150.00)
    
    def test_transaction_creation(self):
        """Test creating transactions"""
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_id='TXN123',
            transaction_type='buy',
            symbol='AAPL',
            quantity=Decimal('5.0'),
            price=Decimal('150.00'),
            amount=Decimal('750.00'),
            fees=Decimal('1.00'),
            transaction_date=timezone.now()
        )
        
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.transaction_type, 'buy')
        self.assertEqual(transaction.symbol, 'AAPL')
        self.assertEqual(float(transaction.amount), 750.00)
    
    def test_brokerage_token_creation(self):
        """Test creating brokerage tokens"""
        token = BrokerageToken.objects.create(
            account=self.account,
            token_type='access',
            token_value='test_token_123',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertEqual(token.account, self.account)
        self.assertEqual(token.token_type, 'access')
        self.assertEqual(token.token_value, 'test_token_123')
    
    def test_service_factory_supported_brokerages(self):
        """Test getting supported brokerages"""
        brokerages = BrokerageServiceFactory.get_supported_brokerages()
        
        self.assertIn('webull', brokerages)
        self.assertIn('robinhood', brokerages)
        self.assertIn('charles_schwab', brokerages)
        self.assertIn('fidelity', brokerages)
    
    def test_service_factory_config(self):
        """Test getting service configuration"""
        config = BrokerageServiceFactory.get_service_config('webull')
        
        self.assertIn('required_fields', config)
        self.assertIn('optional_fields', config)
        self.assertIn('auth_method', config)
        self.assertEqual(config['auth_method'], 'username_password')
    
    def test_service_factory_support_check(self):
        """Test checking if brokerage is supported"""
        self.assertTrue(BrokerageServiceFactory.is_supported('webull'))
        self.assertTrue(BrokerageServiceFactory.is_supported('robinhood'))
        self.assertFalse(BrokerageServiceFactory.is_supported('unsupported_brokerage'))
    
    def test_user_settings_creation(self):
        """Test creating user settings"""
        settings = BrokerageSettings.objects.get(user=self.user)
        
        self.assertEqual(settings.user, self.user)
        self.assertTrue(settings.auto_sync_enabled)
        self.assertEqual(settings.sync_frequency_hours, 24)
        self.assertTrue(settings.price_alerts_enabled)
    
    def test_webhook_creation(self):
        """Test creating webhooks"""
        webhook = BrokerageWebhook.objects.create(
            account=self.account,
            webhook_url='https://example.com/webhook',
            is_active=True
        )
        
        self.assertEqual(webhook.account, self.account)
        self.assertEqual(webhook.webhook_url, 'https://example.com/webhook')
        self.assertTrue(webhook.is_active)
    
    def test_account_status_updates(self):
        """Test updating account status"""
        self.account.status = 'error'
        self.account.last_error = 'Test error message'
        self.account.error_count = 1
        self.account.save()
        
        updated_account = BrokerageAccount.objects.get(id=self.account.id)
        self.assertEqual(updated_account.status, 'error')
        self.assertEqual(updated_account.last_error, 'Test error message')
        self.assertEqual(updated_account.error_count, 1)
    
    def test_portfolio_calculations(self):
        """Test portfolio calculations"""
        # Create multiple positions
        Portfolio.objects.create(
            account=self.account,
            symbol='AAPL',
            quantity=Decimal('10.0'),
            average_price=Decimal('150.00'),
            market_value=Decimal('1600.00'),
            unrealized_pnl=Decimal('100.00')
        )
        
        Portfolio.objects.create(
            account=self.account,
            symbol='GOOGL',
            quantity=Decimal('5.0'),
            average_price=Decimal('2000.00'),
            market_value=Decimal('10500.00'),
            unrealized_pnl=Decimal('500.00')
        )
        
        positions = Portfolio.objects.filter(account=self.account)
        total_market_value = sum(float(pos.market_value or 0) for pos in positions)
        total_unrealized_pnl = sum(float(pos.unrealized_pnl or 0) for pos in positions)
        
        self.assertEqual(total_market_value, 12100.00)
        self.assertEqual(total_unrealized_pnl, 600.00)
    
    def test_transaction_filtering(self):
        """Test transaction filtering"""
        # Create transactions with different dates
        Transaction.objects.create(
            account=self.account,
            transaction_type='buy',
            symbol='AAPL',
            amount=Decimal('750.00'),
            transaction_date=timezone.now() - timedelta(days=5)
        )
        
        Transaction.objects.create(
            account=self.account,
            transaction_type='sell',
            symbol='GOOGL',
            amount=Decimal('1000.00'),
            transaction_date=timezone.now() - timedelta(days=10)
        )
        
        # Test filtering by transaction type
        buy_transactions = Transaction.objects.filter(
            account=self.account, 
            transaction_type='buy'
        )
        self.assertEqual(buy_transactions.count(), 1)
        
        # Test filtering by date range
        recent_transactions = Transaction.objects.filter(
            account=self.account,
            transaction_date__gte=timezone.now() - timedelta(days=7)
        )
        self.assertEqual(recent_transactions.count(), 1)
