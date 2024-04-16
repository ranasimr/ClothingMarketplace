"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from project import views
from django.views.generic import RedirectView
from admin_honeypot import views as honeypot_views

from .views import custom_admin_honeypot_logout, redirect_to_admin_login


urlpatterns = [
    # Other URL patterns...
    
    path('admin/',include('admin_honeypot.urls',namespace='admin_honeypot')),
    path('logout/', custom_admin_honeypot_logout, name='custom_admin_honeypot_logout'),
   path('admin/login/', redirect_to_admin_login, name='admin_honeypot_login_redirect'),
    # Other URL patterns...



    path('securelogin/', admin.site.urls),
    path('',views.homepage,name='homepage'),
    path('store/',include('stores.urls'),name='store'),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
   
    #orders 
    path('orders/', include('orders.urls')),
] +static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)