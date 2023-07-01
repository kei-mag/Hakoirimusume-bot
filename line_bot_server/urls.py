from django.urls import path

from . import views

app_name = 'linebot'
urlpatterns = [
    path('endpoint', views.callback, name='endpoint'),
]
