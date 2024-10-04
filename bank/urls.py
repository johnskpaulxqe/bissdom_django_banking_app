from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='bank/login.html'), name='login'),
    path('logout/', views.logout, name='logout'),
    path('account_balance/', views.account_balance, name='account_balance'),
    path('transfer_money/', views.transfer_money, name='transfer_money'),
    path('add_payee/', views.add_payee, name='add_payee'),
    path('pay_bill/', views.pay_bill, name='pay_bill'),
    path('bill_payment_success/', views.bill_payment_success, name='bill_payment_success'),
    path('api/add_funds/', views.AddFundsAPIView.as_view(), name='add_funds_api'),
    path('api/token/', views.CustomAuthToken.as_view(), name='api_token'),
]
