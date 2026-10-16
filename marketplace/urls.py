from django.urls import path
from .views import SellerProfileView, ItemCreateView, ItemListView, ItemDetailView, MyItemsListView

urlpatterns = [
    # Seller profile routes
    path('sellers/me/', SellerProfileView.as_view(), name='seller-me'),

    # Item routes
    path('items/', ItemListView.as_view(), name='item-list'),              # Public list of active items
    path('items/create/', ItemCreateView.as_view(), name='item-create'),    # Create item (sellers only)
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'), # Retrieve/update/delete item
    path('items/mine/', MyItemsListView.as_view(), name='item-mine'),

]

