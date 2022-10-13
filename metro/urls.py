from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('sensing', views.sensing, name='sensing'),
]
