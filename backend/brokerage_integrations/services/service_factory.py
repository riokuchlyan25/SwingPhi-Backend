from typing import Dict, Any, Optional
from .webull_service import WebullService
from .robinhood_service import RobinhoodService
from .charles_schwab_service import CharlesSchwabService
from .fidelity_service import FidelityService
from .base_service import BaseBrokerageService


class BrokerageServiceFactory:
    """Factory class to create and manage brokerage service instances"""
    
    _services = {
        'webull': WebullService,
        'robinhood': RobinhoodService,
        'charles_schwab': CharlesSchwabService,
        'fidelity': FidelityService,
        # Add other services as they are implemented
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
                'required_fields': ['username', 'password'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'username_password',
                'api_documentation': 'https://webull.com/api'
            },
            'robinhood': {
                'required_fields': ['username', 'password'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'username_password',
                'api_documentation': 'https://robinhood.com/api'
            },
            'charles_schwab': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['access_token'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://schwab.com/api'
            },
            'ibkr': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['access_token'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://interactivebrokers.com/api'
            },
            'fidelity': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['access_token'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://fidelity.com/api'
            },
            'moomoo': {
                'required_fields': ['username', 'password'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'username_password',
                'api_documentation': 'https://moomoo.com/api'
            },
            'sofi': {
                'required_fields': ['username', 'password'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'username_password',
                'api_documentation': 'https://sofi.com/api'
            },
            'etrade': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://etrade.com/api'
            },
            'etoro': {
                'required_fields': ['username', 'password'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'username_password',
                'api_documentation': 'https://etoro.com/api'
            },
            'tradestation': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['access_token', 'refresh_token'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://tradestation.com/api'
            },
            'coinbase': {
                'required_fields': ['api_key', 'secret_key'],
                'optional_fields': ['passphrase'],
                'auth_method': 'api_key_secret',
                'api_documentation': 'https://coinbase.com/api'
            }
        }
        
        return configs.get(brokerage_name.lower(), {}) 