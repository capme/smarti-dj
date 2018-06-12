from . import views
from django.conf.urls import url

urlpatterns = [
    url('^url1', views.url1),
    url('^url2', views.url2)
]
