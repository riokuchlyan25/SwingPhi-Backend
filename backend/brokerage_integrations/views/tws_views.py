"""
Django views for IBKR TWS API integration

These views provide REST API endpoints for accessing IBKR TWS data
through the Django application.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.conf import settings

from ..services.ibkr_tws_service import IBKRTWSService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def tws_account_info(request):
    """Get IBKR TWS account information"""
    try:
        # Get connection parameters from request or use defaults
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        # Create TWS service
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        # Connect to TWS
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway. Ensure TWS is running and API connections are enabled.'
            }, status=503)
        
        try:
            # Get account information
            account_info = tws_service.get_account_info()
            
            return JsonResponse({
                'success': True,
                'data': account_info
            })
            
        finally:
            # Always disconnect
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_account_info: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_account_balance(request):
    """Get IBKR TWS account balance"""
    try:
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            balance = tws_service.get_balance()
            
            return JsonResponse({
                'success': True,
                'data': balance
            })
            
        finally:
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_account_balance: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_portfolio(request):
    """Get IBKR TWS portfolio positions"""
    try:
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            positions = tws_service.get_portfolio()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'positions': positions,
                    'total_positions': len(positions)
                }
            })
            
        finally:
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_portfolio: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_market_data(request):
    """Get IBKR TWS market data for a symbol"""
    try:
        # Get symbol from request
        symbol = request.GET.get('symbol')
        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Symbol parameter is required'
            }, status=400)
        
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        exchange = request.GET.get('exchange', 'SMART')
        currency = request.GET.get('currency', 'USD')
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            market_data = tws_service.get_market_data(
                symbol=symbol,
                exchange=exchange,
                currency=currency
            )
            
            return JsonResponse({
                'success': True,
                'data': market_data
            })
            
        finally:
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_market_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_open_orders(request):
    """Get IBKR TWS open orders"""
    try:
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            open_orders = tws_service.get_open_orders()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'orders': open_orders,
                    'total_orders': len(open_orders)
                }
            })
            
        finally:
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_open_orders: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def tws_place_order(request):
    """Place an order via IBKR TWS"""
    try:
        # Parse request body
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['symbol', 'action', 'quantity', 'order_type']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Get connection parameters
        host = data.get('host', '127.0.0.1')
        port = int(data.get('port', 7497))
        client_id = int(data.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            # Place order
            order_result = tws_service.place_order(
                symbol=data['symbol'],
                action=data['action'],
                quantity=data['quantity'],
                order_type=data['order_type'],
                limit_price=data.get('limit_price'),
                stop_price=data.get('stop_price')
            )
            
            return JsonResponse({
                'success': True,
                'data': order_result
            })
            
        finally:
            tws_service.disconnect()
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in tws_place_order: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def tws_cancel_order(request):
    """Cancel an order via IBKR TWS"""
    try:
        # Parse request body
        data = json.loads(request.body)
        
        # Validate required fields
        if 'order_id' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: order_id'
            }, status=400)
        
        # Get connection parameters
        host = data.get('host', '127.0.0.1')
        port = int(data.get('port', 7497))
        client_id = int(data.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            # Cancel order
            cancel_result = tws_service.cancel_order(data['order_id'])
            
            return JsonResponse({
                'success': True,
                'data': cancel_result
            })
            
        finally:
            tws_service.disconnect()
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in tws_cancel_order: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_connection_status(request):
    """Check TWS connection status"""
    try:
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        # Test connection
        is_connected = tws_service.authenticate()
        
        if is_connected:
            tws_service.disconnect()
        
        return JsonResponse({
            'success': True,
            'data': {
                'connected': is_connected,
                'host': host,
                'port': port,
                'client_id': client_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error in tws_connection_status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def tws_account_summary(request):
    """Get comprehensive account summary from TWS"""
    try:
        # Get connection parameters
        host = request.GET.get('host', '127.0.0.1')
        port = int(request.GET.get('port', 7497))
        client_id = int(request.GET.get('client_id', 1))
        
        tws_service = IBKRTWSService(
            host=host,
            port=port,
            client_id=client_id
        )
        
        if not tws_service.authenticate():
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to TWS/Gateway'
            }, status=503)
        
        try:
            # Get all account data
            account_info = tws_service.get_account_info()
            balance = tws_service.get_balance()
            positions = tws_service.get_portfolio()
            open_orders = tws_service.get_open_orders()
            
            # Calculate portfolio summary
            total_value = 0
            total_pnl = 0
            for position in positions:
                if position.get('market_value'):
                    total_value += float(position['market_value'])
                if position.get('unrealized_pnl'):
                    total_pnl += float(position['unrealized_pnl'])
            
            summary = {
                'account_info': account_info,
                'balance': balance,
                'portfolio': {
                    'positions': positions,
                    'total_positions': len(positions),
                    'total_market_value': total_value,
                    'total_unrealized_pnl': total_pnl
                },
                'orders': {
                    'open_orders': open_orders,
                    'total_open_orders': len(open_orders)
                },
                'connection': {
                    'host': host,
                    'port': port,
                    'client_id': client_id,
                    'connected': True
                }
            }
            
            return JsonResponse({
                'success': True,
                'data': summary
            })
            
        finally:
            tws_service.disconnect()
            
    except Exception as e:
        logger.error(f"Error in tws_account_summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
