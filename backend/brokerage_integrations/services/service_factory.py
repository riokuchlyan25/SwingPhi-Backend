from typing import Dict, Any, Optional
from .webull_service import WebullService
from .robinhood_service import RobinhoodService
from .charles_schwab_service import CharlesSchwabService
from .fidelity_service import FidelityService
from .ibkr_service import IBKRService
from .ibkr_tws_service import IBKRTWSService
from .moomoo_service import MoomooService
from .sofi_service import SoFiService
from .etrade_service import ETradeService
from .etoro_service import EToroService
from .tradestation_service import TradeStationService
from .coinbase_service import CoinbaseService
from .base_service import BaseBrokerageService


class BrokerageServiceFactory:
    """Factory class to create and manage brokerage service instances"""
    
    _services = {
        'webull': WebullService,
        'robinhood': RobinhoodService,
        'charles_schwab': CharlesSchwabService,
        'fidelity': FidelityService,
        'ibkr': IBKRService,
        'ibkr_tws': IBKRTWSService,
        'moomoo': MoomooService,
        'sofi': SoFiService,
        'etrade': ETradeService,
        'etoro': EToroService,
        'tradestation': TradeStationService,
        'coinbase': CoinbaseService,
    }
    
    @classmethod
    def create_service(cls, brokerage_name: str, **kwargs) -> Optional[BaseBrokerageService]:
        """Create a brokerage service instance"""
        service_class = cls._services.get(brokerage_name.lower())
        if service_class:
            return service_class(**kwargs)
        return None
    
    @classmethod
    def get_supported_brokerages(cls) -> list:
        """Get list of supported brokerage platforms"""
        return list(cls._services.keys())
    
    @classmethod
    def is_supported(cls, brokerage_name: str) -> bool:
        """Check if a brokerage is supported"""
        return brokerage_name.lower() in cls._services
    
    @classmethod
    def get_service_config(cls, brokerage_name: str) -> Dict[str, Any]:
        """Get configuration requirements for a brokerage service"""
        configs = {
            'webull': {
                'required_fields': ['app_key', 'app_secret'],
                'optional_fields': [],
                'auth_method': 'webull_openapi',
                'api_documentation': 'https://developer.webull.com/',
                'notes': 'Requires developer approval; use SDK after App Key/Secret issued.'
            },
            'robinhood': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'aggregator',
                'api_documentation': 'https://plaid.com/ | https://www.snaptrade.com/',
                'notes': 'No public API; use Plaid or SnapTrade.'
            },
            'charles_schwab': {
                'required_fields': ['oauth_client_id', 'oauth_client_secret'],
                'optional_fields': [],
                'auth_method': 'oauth',
                'api_documentation': 'https://developer.schwab.com/',
                'notes': 'Requires app registration and approval.'
            },
            'ibkr': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'client_portal_or_tws',
                'api_documentation': 'https://www.interactivebrokers.com/en/trading/ib-api.php',
                'notes': 'Use Client Portal REST or TWS API (ibapi) with Gateway/TWS running.'
            },
            'ibkr_tws': {
                'required_fields': [],
                'optional_fields': ['host', 'port', 'client_id'],
                'auth_method': 'tws_gateway',
                'api_documentation': 'https://www.interactivebrokers.com/en/trading/ib-api.php',
                'notes': 'Requires TWS or Gateway running locally. Default: localhost:7497 (TWS) or localhost:4001 (Gateway).'
            },
            'fidelity': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'aggregator',
                'api_documentation': 'https://www.snaptrade.com/ | https://plaid.com/',
                'notes': 'Fidelity Access for authorized partners; use aggregator.'
            },
            'moomoo': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'futu_opend_gateway',
                'api_documentation': 'https://openapi.futunn.com/futu-api-doc/intro/en/',
                'notes': 'Requires local OpenD + futu SDK.'
            },
            'sofi': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'aggregator',
                'api_documentation': 'https://plaid.com/',
                'notes': 'No public API; use Plaid.'
            },
            'etrade': {
                'required_fields': ['oauth_client_id', 'oauth_client_secret'],
                'optional_fields': [],
                'auth_method': 'oauth',
                'api_documentation': 'https://developer.etrade.com/',
                'notes': 'Requires developer app and OAuth keys.'
            },
            'etoro': {
                'required_fields': [],
                'optional_fields': [],
                'auth_method': 'aggregator',
                'api_documentation': 'https://www.snaptrade.com/ | https://vezgo.com/',
                'notes': 'No public API as of 2025; use aggregator.'
            },
            'tradestation': {
                'required_fields': ['oauth_client_id', 'oauth_client_secret'],
                'optional_fields': [],
                'auth_method': 'oauth',
                'api_documentation': 'https://developer.tradestation.com/',
                'notes': 'Users can generate API keys for personal use; OAuth required.'
            },
            'coinbase': {
                'required_fields': ['api_key', 'api_secret', 'passphrase'],
                'optional_fields': [],
                'auth_method': 'api_key',
                'api_documentation': 'https://docs.cdp.coinbase.com/advanced-trade/docs/welcome',
                'notes': 'Open to users via API key/secret/passphrase.'
            }
        }
        
        return configs.get(brokerage_name.lower(), {}) 