"""
URL configuration for C2B project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from payments.views import stk_push, get_access_token, stkpush_callback,stkpush_status, c2b_url_registration, c2bpayment_confirmation



urlpatterns = [
    path('admin/', admin.site.urls),
    path('mpesa/access-token/', get_access_token),
    path('mpesa/stk-push/', stk_push),
    path('mpesa/stkpush-status/', stkpush_status),
    path('mpesa/stkpush-callback/', stkpush_callback), 
    path('mpesa/c2b-url-registration/', c2b_url_registration),
    path('mpesa/c2b-payment-confirmation/', c2bpayment_confirmation),
    
]
