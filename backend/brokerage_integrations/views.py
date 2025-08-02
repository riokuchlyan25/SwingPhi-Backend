from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    BrokerageAccount, BrokerageToken, Portfolio, Transaction, 
    BrokerageWebhook, BrokerageSettings
)
from .services.service_factory import BrokerageServiceFactory

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_supported_brokerages(request):
    """Get list of supported brokerage platforms"""
    try:
        brokerages = BrokerageServiceFactory.get_supported_brokerages()
        configs = {}
        
        for brokerage in brokerages:
            configs[brokerage] = BrokerageServiceFactory.get_service_config(brokerage)
        
        return JsonResponse({
            'success': True,
            'brokerages': brokerages,
            'configurations': configs
        })
    except Exception as e:
        logger.error(f"Error getting supported brokerages: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def connect_brokerage_account(request):
    """Connect a new brokerage account"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        brokerage_name = data.get('brokerage_name')
        credentials = data.get('credentials', {})
        
        if not user_id or not brokerage_name:
            return JsonResponse({
                'success': False,
                'error': 'user_id and brokerage_name are required'
            }, status=400)
        
        # Check if brokerage is supported
        if not BrokerageServiceFactory.is_supported(brokerage_name):
            return JsonResponse({
                'success': False,
                'error': f'Brokerage {brokerage_name} is not supported'
            }, status=400)
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # Check if account already exists
        existing_account = BrokerageAccount.objects.filter(
            user=user, 
            brokerage_name=brokerage_name
        ).first()
        
        if existing_account:
            return JsonResponse({
                'success': False,
                'error': f'Account for {brokerage_name} already exists'
            }, status=400)
        
        # Create service instance to test connection
        service = BrokerageServiceFactory.create_service(
            brokerage_name, 
            account_id=credentials.get('account_id', ''),
            **credentials
        )
        
        if not service:
            return JsonResponse({
                'success': False,
                'error': f'Failed to create service for {brokerage_name}'
            }, status=500)
        
        # Test authentication
        if not service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Authentication failed. Please check your credentials.'
            }, status=401)
        
        # Get account info
        account_info = service.get_account_info()
        if not account_info.get('success'):
            return JsonResponse({
                'success': False,
                'error': 'Failed to get account information'
            }, status=500)
        
        # Create brokerage account
        with transaction.atomic():
            account = BrokerageAccount.objects.create(
                user=user,
                brokerage_name=brokerage_name,
                account_id=account_info['data'].get('account_id', ''),
                account_name=account_info['data'].get('account_name', ''),
                status='connected'
            )
            
            # Store tokens if available
            if service.access_token:
                BrokerageToken.objects.create(
                    account=account,
                    token_type='access',
                    token_value=service.access_token,
                    expires_at=timezone.now() + timedelta(hours=24)  # Default expiry
                )
            
            if service.refresh_token:
                BrokerageToken.objects.create(
                    account=account,
                    token_type='refresh',
                    token_value=service.refresh_token
                )
            
            # Create default settings
            BrokerageSettings.objects.get_or_create(user=user)
        
        return JsonResponse({
            'success': True,
            'account_id': str(account.id),
            'message': f'Successfully connected {brokerage_name} account'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error connecting brokerage account: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_accounts(request, user_id):
    """Get all brokerage accounts for a user"""
    try:
        accounts = BrokerageAccount.objects.filter(user_id=user_id, is_active=True)
        
        account_data = []
        for account in accounts:
            account_data.append({
                'id': str(account.id),
                'brokerage_name': account.brokerage_name,
                'account_id': account.account_id,
                'account_name': account.account_name,
                'status': account.status,
                'created_at': account.created_at.isoformat(),
                'last_sync': account.last_sync.isoformat() if account.last_sync else None,
                'cash_balance': float(account.cash_balance) if account.cash_balance else None,
                'total_value': float(account.total_value) if account.total_value else None,
                'buying_power': float(account.buying_power) if account.buying_power else None
            })
        
        return JsonResponse({
            'success': True,
            'accounts': account_data
        })
        
    except Exception as e:
        logger.error(f"Error getting user accounts: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sync_account(request, account_id):
    """Sync a specific brokerage account"""
    try:
        data = json.loads(request.body)
        force_sync = data.get('force_sync', False)
        
        try:
            account = BrokerageAccount.objects.get(id=account_id)
        except BrokerageAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Account not found'
            }, status=404)
        
        # Check if sync is needed (unless forced)
        if not force_sync and account.last_sync:
            time_since_sync = timezone.now() - account.last_sync
            if time_since_sync.total_seconds() < 3600:  # 1 hour
                return JsonResponse({
                    'success': False,
                    'error': 'Account was synced recently. Use force_sync=true to override.'
                }, status=400)
        
        # Get service instance
        tokens = {token.token_type: token.token_value for token in account.tokens.all()}
        
        service = BrokerageServiceFactory.create_service(
            account.brokerage_name,
            account_id=account.account_id,
            **tokens
        )
        
        if not service:
            return JsonResponse({
                'success': False,
                'error': f'Failed to create service for {account.brokerage_name}'
            }, status=500)
        
        # Test authentication
        if not service.authenticate():
            account.status = 'error'
            account.last_error = 'Authentication failed'
            account.error_count += 1
            account.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Authentication failed'
            }, status=401)
        
        # Sync data
        with transaction.atomic():
            # Update account status
            account.status = 'connected'
            account.last_sync = timezone.now()
            account.error_count = 0
            account.last_error = None
            
            # Get and update balance
            balance_data = service.get_balance()
            if balance_data.get('success'):
                balance = balance_data['data']
                account.cash_balance = balance.get('cash_balance')
                account.total_value = balance.get('total_value')
                account.buying_power = balance.get('buying_power')
            
            account.save()
            
            # Sync portfolio
            portfolio_data = service.get_portfolio()
            if portfolio_data:
                # Clear existing portfolio
                Portfolio.objects.filter(account=account).delete()
                
                # Create new portfolio entries
                for position in portfolio_data:
                    Portfolio.objects.create(
                        account=account,
                        symbol=position['symbol'],
                        quantity=position['quantity'],
                        average_price=position['average_price'],
                        current_price=position['current_price'],
                        market_value=position['market_value'],
                        unrealized_pnl=position['unrealized_pnl'],
                        unrealized_pnl_percent=position['unrealized_pnl_percent']
                    )
            
            # Sync transactions (last 30 days)
            transactions_data = service.get_transactions(
                start_date=timezone.now() - timedelta(days=30)
            )
            
            if transactions_data:
                # Only add new transactions
                existing_transaction_ids = set(
                    Transaction.objects.filter(account=account)
                    .values_list('transaction_id', flat=True)
                )
                
                for transaction_data in transactions_data:
                    if transaction_data['transaction_id'] not in existing_transaction_ids:
                        Transaction.objects.create(
                            account=account,
                            transaction_id=transaction_data['transaction_id'],
                            transaction_type=transaction_data['transaction_type'],
                            symbol=transaction_data['symbol'],
                            quantity=transaction_data['quantity'],
                            price=transaction_data['price'],
                            amount=transaction_data['amount'],
                            fees=transaction_data['fees'],
                            transaction_date=transaction_data['transaction_date']
                        )
        
        return JsonResponse({
            'success': True,
            'message': 'Account synced successfully',
            'portfolio_count': len(portfolio_data) if portfolio_data else 0,
            'transactions_count': len(transactions_data) if transactions_data else 0
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error syncing account: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_portfolio(request, account_id):
    """Get portfolio for a specific account"""
    try:
        try:
            account = BrokerageAccount.objects.get(id=account_id)
        except BrokerageAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Account not found'
            }, status=404)
        
        portfolio = Portfolio.objects.filter(account=account)
        
        portfolio_data = []
        for position in portfolio:
            portfolio_data.append({
                'symbol': position.symbol,
                'quantity': float(position.quantity),
                'average_price': float(position.average_price),
                'current_price': float(position.current_price) if position.current_price else None,
                'market_value': float(position.market_value) if position.market_value else None,
                'unrealized_pnl': float(position.unrealized_pnl) if position.unrealized_pnl else None,
                'unrealized_pnl_percent': float(position.unrealized_pnl_percent) if position.unrealized_pnl_percent else None,
                'last_updated': position.last_updated.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'account_id': str(account.id),
            'brokerage_name': account.brokerage_name,
            'portfolio': portfolio_data
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_transactions(request, account_id):
    """Get transactions for a specific account"""
    try:
        try:
            account = BrokerageAccount.objects.get(id=account_id)
        except BrokerageAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Account not found'
            }, status=404)
        
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        transaction_type = request.GET.get('transaction_type')
        
        transactions = Transaction.objects.filter(account=account)
        
        # Apply filters
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                transactions = transactions.filter(transaction_date__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                transactions = transactions.filter(transaction_date__lte=end_dt)
            except ValueError:
                pass
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        transactions_data = []
        for transaction in transactions:
            transactions_data.append({
                'transaction_id': transaction.transaction_id,
                'transaction_type': transaction.transaction_type,
                'symbol': transaction.symbol,
                'quantity': float(transaction.quantity) if transaction.quantity else None,
                'price': float(transaction.price) if transaction.price else None,
                'amount': float(transaction.amount),
                'fees': float(transaction.fees),
                'transaction_date': transaction.transaction_date.isoformat(),
                'created_at': transaction.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'account_id': str(account.id),
            'brokerage_name': account.brokerage_name,
            'transactions': transactions_data
        })
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def disconnect_account(request, account_id):
    """Disconnect a brokerage account"""
    try:
        try:
            account = BrokerageAccount.objects.get(id=account_id)
        except BrokerageAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Account not found'
            }, status=404)
        
        # Soft delete - mark as inactive
        account.is_active = False
        account.status = 'disconnected'
        account.save()
        
        # Delete associated tokens
        account.tokens.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully disconnected {account.brokerage_name} account'
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting account: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
