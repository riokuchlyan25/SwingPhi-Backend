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

        # Gate connection based on real integration path per research
        config = BrokerageServiceFactory.get_service_config(brokerage_name)
        auth_method = (config or {}).get('auth_method')
        guidance = (config or {}).get('notes') or ''

        # Only allow direct connect for brokerages with implemented direct API (Coinbase)
        if auth_method in ['aggregator', 'futu_opend_gateway', 'webull_openapi', 'oauth', 'client_portal_or_tws']:
            return JsonResponse({
                'success': False,
                'error': f'Connection for {brokerage_name} is not available directly from backend.',
                'requires': auth_method,
                'guidance': guidance or 'Use an approved developer app or a data aggregator (Plaid/SnapTrade).'
            }, status=501)
        
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
        
        # Create service instance to test connection (direct integrations only)
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


@csrf_exempt
@require_http_methods(["GET"])
def get_brokerage_link(request, brokerage_name):
    """Get login link for a specific brokerage"""
    try:
        # Check if brokerage is supported
        if not BrokerageServiceFactory.is_supported(brokerage_name):
            return JsonResponse({
                'success': False,
                'error': f'Brokerage {brokerage_name} is not supported'
            }, status=400)
        
        # Define static login links for each brokerage
        brokerage_links = {
            'webull': 'https://www.webull.com/login',
            'robinhood': 'https://robinhood.com/login',
            'ibkr': 'https://www.interactivebrokers.com/portal/main',
            'charles_schwab': 'https://www.schwab.com/login',
            'fidelity': 'https://www.fidelity.com/login',
            'moomoo': 'https://www.moomoo.com/login',
            'sofi': 'https://www.sofi.com/login',
            'etrade': 'https://us.etrade.com/login',
            'etoro': 'https://www.etoro.com/login',
            'tradestation': 'https://www.tradestation.com/login',
            'coinbase': 'https://www.coinbase.com/login'
        }
        
        link = brokerage_links.get(brokerage_name.lower())
        if not link:
            return JsonResponse({
                'success': False,
                'error': f'No login link found for {brokerage_name}'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'brokerage_name': brokerage_name,
            'login_link': link
        })
        
    except Exception as e:
        logger.error(f"Error getting brokerage link: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_aggregated_portfolio(request, user_id):
    """Get aggregated portfolio across all user's brokerage accounts"""
    try:
        accounts = BrokerageAccount.objects.filter(user_id=user_id, is_active=True, status='connected')
        
        aggregated_portfolio = {}
        total_value = Decimal('0')
        
        for account in accounts:
            # Get portfolio for this account
            portfolio = Portfolio.objects.filter(account=account)
            
            for position in portfolio:
                symbol = position.symbol
                
                if symbol not in aggregated_portfolio:
                    aggregated_portfolio[symbol] = {
                        'symbol': symbol,
                        'total_quantity': Decimal('0'),
                        'total_market_value': Decimal('0'),
                        'positions': []
                    }
                
                # Add position data
                aggregated_portfolio[symbol]['total_quantity'] += position.quantity
                aggregated_portfolio[symbol]['total_market_value'] += position.market_value or Decimal('0')
                aggregated_portfolio[symbol]['positions'].append({
                    'brokerage': account.brokerage_name,
                    'quantity': float(position.quantity),
                    'average_price': float(position.average_price),
                    'current_price': float(position.current_price) if position.current_price else None,
                    'market_value': float(position.market_value) if position.market_value else None,
                    'unrealized_pnl': float(position.unrealized_pnl) if position.unrealized_pnl else None,
                    'unrealized_pnl_percent': float(position.unrealized_pnl_percent) if position.unrealized_pnl_percent else None
                })
                
                total_value += position.market_value or Decimal('0')
        
        # Convert to list and sort by market value
        portfolio_list = list(aggregated_portfolio.values())
        portfolio_list.sort(key=lambda x: x['total_market_value'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'user_id': user_id,
            'total_portfolio_value': float(total_value),
            'portfolio': portfolio_list
        })
        
    except Exception as e:
        logger.error(f"Error getting aggregated portfolio: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_aggregated_balance(request, user_id):
    """Get aggregated balance across all user's brokerage accounts"""
    try:
        accounts = BrokerageAccount.objects.filter(user_id=user_id, is_active=True, status='connected')
        
        total_cash_balance = Decimal('0')
        total_portfolio_value = Decimal('0')
        total_buying_power = Decimal('0')
        
        account_balances = []
        
        for account in accounts:
            account_balance = {
                'brokerage_name': account.brokerage_name,
                'account_id': str(account.id),
                'cash_balance': float(account.cash_balance) if account.cash_balance else 0,
                'total_value': float(account.total_value) if account.total_value else 0,
                'buying_power': float(account.buying_power) if account.buying_power else 0
            }
            
            total_cash_balance += account.cash_balance or Decimal('0')
            total_portfolio_value += account.total_value or Decimal('0')
            total_buying_power += account.buying_power or Decimal('0')
            
            account_balances.append(account_balance)
        
        return JsonResponse({
            'success': True,
            'user_id': user_id,
            'total_cash_balance': float(total_cash_balance),
            'total_portfolio_value': float(total_portfolio_value),
            'total_buying_power': float(total_buying_power),
            'account_balances': account_balances
        })
        
    except Exception as e:
        logger.error(f"Error getting aggregated balance: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_aggregated_transactions(request, user_id):
    """Get aggregated transactions across all user's brokerage accounts"""
    try:
        accounts = BrokerageAccount.objects.filter(user_id=user_id, is_active=True, status='connected')
        
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        transaction_type = request.GET.get('transaction_type')
        
        all_transactions = []
        
        for account in accounts:
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
            
            for transaction in transactions:
                all_transactions.append({
                    'transaction_id': transaction.transaction_id,
                    'brokerage_name': account.brokerage_name,
                    'transaction_type': transaction.transaction_type,
                    'symbol': transaction.symbol,
                    'quantity': float(transaction.quantity) if transaction.quantity else None,
                    'price': float(transaction.price) if transaction.price else None,
                    'amount': float(transaction.amount),
                    'fees': float(transaction.fees),
                    'transaction_date': transaction.transaction_date.isoformat(),
                    'created_at': transaction.created_at.isoformat()
                })
        
        # Sort by transaction date (newest first)
        all_transactions.sort(key=lambda x: x['transaction_date'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'user_id': user_id,
            'transactions': all_transactions
        })
        
    except Exception as e:
        logger.error(f"Error getting aggregated transactions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Individual brokerage data routes
@csrf_exempt
@require_http_methods(["GET"])
def get_webull_data(request):
    """Get Webull brokerage data.

    Per research: Webull requires approved OpenAPI access via their
    developer portal (App Key/Secret). Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'webull',
            'requires': 'Webull OpenAPI (App Key/Secret, approval required)',
            'how_to_connect': 'Apply at developer.webull.com → OpenAPI Management → generate App Key/Secret → use their SDK.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting Webull data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_robinhood_data(request):
    """Get Robinhood brokerage data.

    Per research: No public API. Use a data aggregator (Plaid/SnapTrade).
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'robinhood',
            'requires': 'Aggregator (Plaid or SnapTrade)',
            'how_to_connect': 'Integrate an aggregator that supports Robinhood OAuth (e.g., SnapTrade/Plaid).',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting Robinhood data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_ibkr_data(request):
    """Get Interactive Brokers (IBKR) brokerage data.

    Per research: Use IBKR Client Portal API or TWS API (ibapi) with TWS/Gateway running.
    This backend route returns guidance rather than attempting live calls.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'ibkr',
            'requires': 'IBKR Client Portal API or TWS API (no third-party approval)',
            'how_to_connect': 'Run IB Gateway/TWS and use Client Portal REST or ibapi to fetch balances/positions.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting IBKR data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_charles_schwab_data(request):
    """Get Charles Schwab brokerage data.

    Per research: Requires Schwab Developer Portal app + OAuth approval.
    Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'charles_schwab',
            'requires': 'Schwab Developer Portal app + OAuth (review/approval)',
            'how_to_connect': 'Register at developer.schwab.com, request Accounts & Trading APIs, complete OAuth flow.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting Charles Schwab data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_fidelity_data(request):
    """Get Fidelity brokerage data.

    Per research: Fidelity Access is available via authorized partners only.
    Use SnapTrade or Plaid. Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'fidelity',
            'requires': 'Fidelity Access via authorized partner',
            'how_to_connect': 'Use an aggregator (e.g., SnapTrade/Plaid) to link Fidelity accounts.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting Fidelity data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_moomoo_data(request):
    """Get Moomoo brokerage data.

    Per research: Use Futu OpenD gateway + futu SDK locally. Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'moomoo',
            'requires': 'Futu OpenD gateway + futu Python SDK',
            'how_to_connect': 'Run OpenD locally and use futu OpenSecTradeContext.position_list_query().',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting Moomoo data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_sofi_data(request):
    """Get SoFi brokerage data.

    Per research: No public API. Use aggregator (Plaid). Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'sofi',
            'requires': 'Aggregator (Plaid/SnapTrade)',
            'how_to_connect': 'Integrate Plaid/SnapTrade to link SoFi Invest.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting SoFi data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_etrade_data(request):
    """Get E-Trade brokerage data.

    Per research: Requires E*TRADE developer account/app and OAuth keys.
    Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'etrade',
            'requires': 'E*TRADE Developer app + OAuth keys',
            'how_to_connect': 'Register at developer.etrade.com, create an app, obtain OAuth keys, then call balances/positions endpoints.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting E-Trade data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_etoro_data(request):
    """Get eToro brokerage data.

    Per research (2025): No public API. Use an aggregator. Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'etoro',
            'requires': 'Aggregator (Plaid/SnapTrade/Vezgo)',
            'how_to_connect': 'Use a data aggregator that supports eToro connections.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting eToro data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_tradestation_data(request):
    """Get TradeStation brokerage data.

    Per research: Requires TradeStation Developer API keys + OAuth. Return guidance.
    """
    try:
        return JsonResponse({
            'success': False,
            'brokerage': 'tradestation',
            'requires': 'TradeStation Developer API keys + OAuth',
            'how_to_connect': 'Sign up at developer.tradestation.com, create an app, obtain client keys, integrate OAuth and call balances/positions.',
            'status': 'not_implemented'
        }, status=501)
    except Exception as e:
        logger.error(f"Error getting TradeStation data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_coinbase_data(request):
    """Get Coinbase brokerage data"""
    try:
        # Get query parameters for authentication
        api_key = request.GET.get('api_key')
        secret_key = request.GET.get('secret_key')
        passphrase = request.GET.get('passphrase')
        account_id = request.GET.get('account_id', 'default')
        
        if not api_key or not secret_key or not passphrase:
            return JsonResponse({
                'success': False,
                'error': 'api_key, secret_key, and passphrase are required'
            }, status=400)
        
        # Create service instance
        service = BrokerageServiceFactory.create_service(
            'coinbase',
            account_id=account_id,
            api_key=api_key,
            secret_key=secret_key,
            passphrase=passphrase
        )
        
        if not service:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create Coinbase service'
            }, status=500)
        
        # Get data
        account_info = service.get_account_info()
        portfolio = service.get_portfolio()
        balance = service.get_balance()
        transactions = service.get_transactions()
        
        return JsonResponse({
            'success': True,
            'brokerage': 'coinbase',
            'account_info': account_info,
            'portfolio': portfolio,
            'balance': balance,
            'transactions': transactions
        })
        
    except Exception as e:
        logger.error(f"Error getting Coinbase data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
