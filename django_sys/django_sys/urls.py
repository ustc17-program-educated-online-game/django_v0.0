"""django_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import include
from login import views as views1
from game import views as views2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views1.index),
    path('login/', views1.login),
    path('register/', views1.register),
    path('logout/', views1.logout),
    path('captcha/', include('captcha.urls')),
    path('confirm/', views1.user_confirm),
    path('guest/', views1.guest),
    path('game/', views2.game),
    path('map/',views2.map_info)
]
