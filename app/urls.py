from . import views
from django.conf.urls import url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = []
urlpatterns += format_suffix_patterns([
    url(r'/url1', views.url1),
])
urlpatterns += router.urls
