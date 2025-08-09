from django.urls import path
from . import views

urlpatterns = [
    # Brokerage management
    path('brokerages/supported/', views.get_supported_brokerages, name='get_supported_brokerages'),
    path('brokerages/connect/', views.connect_brokerage_account, name='connect_brokerage_account'),
    path('brokerages/user/<int:user_id>/accounts/', views.get_user_accounts, name='get_user_accounts'),
    path('brokerages/accounts/<uuid:account_id>/sync/', views.sync_account, name='sync_account'),
    path('brokerages/accounts/<uuid:account_id>/disconnect/', views.disconnect_account, name='disconnect_account'),
    
    # Portfolio and transactions
    path('brokerages/accounts/<uuid:account_id>/portfolio/', views.get_portfolio, name='get_portfolio'),
    path('brokerages/accounts/<uuid:account_id>/transactions/', views.get_transactions, name='get_transactions'),
    
    # Brokerage links
    path('brokerages/<str:brokerage_name>/link/', views.get_brokerage_link, name='get_brokerage_link'),
    
    # Aggregated data
    path('brokerages/user/<int:user_id>/aggregated/portfolio/', views.get_aggregated_portfolio, name='get_aggregated_portfolio'),
    path('brokerages/user/<int:user_id>/aggregated/balance/', views.get_aggregated_balance, name='get_aggregated_balance'),
    path('brokerages/user/<int:user_id>/aggregated/transactions/', views.get_aggregated_transactions, name='get_aggregated_transactions'),
    
    # Individual brokerage data routes
    path('brokerages/webull/data/', views.get_webull_data, name='get_webull_data'),
    path('brokerages/robinhood/data/', views.get_robinhood_data, name='get_robinhood_data'),
    path('brokerages/ibkr/data/', views.get_ibkr_data, name='get_ibkr_data'),
    path('brokerages/charles_schwab/data/', views.get_charles_schwab_data, name='get_charles_schwab_data'),
    path('brokerages/fidelity/data/', views.get_fidelity_data, name='get_fidelity_data'),
    path('brokerages/moomoo/data/', views.get_moomoo_data, name='get_moomoo_data'),
    path('brokerages/sofi/data/', views.get_sofi_data, name='get_sofi_data'),
    path('brokerages/etrade/data/', views.get_etrade_data, name='get_etrade_data'),
    path('brokerages/etoro/data/', views.get_etoro_data, name='get_etoro_data'),
    path('brokerages/tradestation/data/', views.get_tradestation_data, name='get_tradestation_data'),
    path('brokerages/coinbase/data/', views.get_coinbase_data, name='get_coinbase_data'),
] 