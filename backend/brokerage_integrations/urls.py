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
] 