from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BrokerageAccount, BrokerageToken, Portfolio, Transaction, 
    BrokerageWebhook, BrokerageSettings
)


@admin.register(BrokerageAccount)
class BrokerageAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'brokerage_name', 'account_name', 'status', 'is_active', 'created_at', 'last_sync')
    list_filter = ('brokerage_name', 'status', 'is_active', 'created_at')
    search_fields = ('user__username', 'account_name', 'account_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_sync', 'error_count')
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'brokerage_name', 'account_id', 'account_name', 'status', 'is_active')
        }),
        ('Balance Information', {
            'fields': ('cash_balance', 'total_value', 'buying_power'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'last_sync', 'error_count', 'last_error'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BrokerageToken)
class BrokerageTokenAdmin(admin.ModelAdmin):
    list_display = ('account', 'token_type', 'created_at', 'expires_at')
    list_filter = ('token_type', 'created_at')
    search_fields = ('account__user__username', 'account__brokerage_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account__user')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('account', 'symbol', 'quantity', 'average_price', 'market_value', 'unrealized_pnl_percent', 'last_updated')
    list_filter = ('account__brokerage_name', 'last_updated')
    search_fields = ('symbol', 'account__user__username')
    readonly_fields = ('id', 'last_updated')
    
    fieldsets = (
        ('Position Information', {
            'fields': ('account', 'symbol', 'quantity', 'average_price', 'current_price')
        }),
        ('Value Information', {
            'fields': ('market_value', 'unrealized_pnl', 'unrealized_pnl_percent')
        }),
        ('System Information', {
            'fields': ('id', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account__user')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'symbol', 'quantity', 'price', 'amount', 'transaction_date')
    list_filter = ('transaction_type', 'account__brokerage_name', 'transaction_date', 'created_at')
    search_fields = ('symbol', 'transaction_id', 'account__user__username')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('account', 'transaction_id', 'transaction_type', 'symbol', 'quantity', 'price', 'amount', 'fees', 'transaction_date')
        }),
        ('System Information', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account__user')


@admin.register(BrokerageWebhook)
class BrokerageWebhookAdmin(admin.ModelAdmin):
    list_display = ('account', 'webhook_url', 'is_active', 'created_at', 'last_triggered')
    list_filter = ('is_active', 'created_at', 'account__brokerage_name')
    search_fields = ('webhook_url', 'account__user__username')
    readonly_fields = ('id', 'created_at', 'last_triggered')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account__user')


@admin.register(BrokerageSettings)
class BrokerageSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'auto_sync_enabled', 'sync_frequency_hours', 'price_alerts_enabled', 'portfolio_alerts_enabled')
    list_filter = ('auto_sync_enabled', 'price_alerts_enabled', 'portfolio_alerts_enabled', 'transaction_notifications_enabled')
    search_fields = ('user__username',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Sync Preferences', {
            'fields': ('user', 'auto_sync_enabled', 'sync_frequency_hours')
        }),
        ('Notification Preferences', {
            'fields': ('price_alerts_enabled', 'portfolio_alerts_enabled', 'transaction_notifications_enabled')
        }),
        ('Privacy Settings', {
            'fields': ('share_portfolio_data', 'share_transaction_data')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
