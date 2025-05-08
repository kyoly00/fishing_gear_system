from django.urls import path
from .views import gear_list_view, losting_gear_view

urlpatterns = [
    path('',            gear_list_view,   name='gear_list'),
    path('losting-gear/', losting_gear_view, name='losting_gear'),
]