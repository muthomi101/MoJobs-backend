from django.urls import path
from .views import (
    RegisterView, LoginView,
    FundiProfileView, FundiDeleteView, FundiPublicList, FundiPublicDetail,
    ClientRegisterView, ClientLoginView, ClientListView, ClientMeView,
    FundiResetPasswordView, ClientResetPasswordView,
    HealthCheckView,
    SellerProfileView
)

urlpatterns = [
    # --------------------------
    # Fundi URLs
    # --------------------------
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('fundis/me/', FundiProfileView.as_view()),
    path('fundis/me/delete/', FundiDeleteView.as_view()),
    path('fundis/', FundiPublicList.as_view()),
    path('fundis/<int:pk>/', FundiPublicDetail.as_view()),
    path('reset-password/', FundiResetPasswordView.as_view(), name='reset-password'),

    # --------------------------
    # Client URLs
    # --------------------------
    path('clients/register/', ClientRegisterView.as_view(), name='client-register'),
    path('clients/login/', ClientLoginView.as_view(), name='client-login'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/me/', ClientMeView.as_view(), name='client-me'),
    path('clients/reset-password/', ClientResetPasswordView.as_view(), name='client-reset-password'),

    # --------------------------
    # Seller URLs
    # --------------------------
    path('sellers/me/', SellerProfileView.as_view(), name='seller-me'),

    # --------------------------
    # Health
    # --------------------------
    path("health/", HealthCheckView.as_view(), name="health"),
]

