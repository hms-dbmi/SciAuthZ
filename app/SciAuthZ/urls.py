"""SciAuthZ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.defaults import page_not_found
from django.contrib import admin

from rest_framework import routers
from authorization import views
from .views import ht

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'user_permission', views.UserPermissionViewSet)

urlpatterns = [
    url(r'^admin/login/', page_not_found, {'exception': Exception('Admin form login disabled.')}),
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^ht/', ht),
    url(r'^', include(router.urls))
]