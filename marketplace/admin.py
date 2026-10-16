from django.contrib import admin
from .models import SellerProfile, Item

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'is_verified', 'created_at')
    search_fields = ('user__name', 'user__phone_number', 'location')
    list_filter = ('is_verified',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'is_paid', 'is_active', 'created_at')
    search_fields = ('title', 'seller__user__name')
    list_filter = ('category', 'is_paid', 'is_active')

