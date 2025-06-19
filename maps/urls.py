from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('simulate/', views.simulate_drift, name='simulate_drift'),
]