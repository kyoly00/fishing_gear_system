from django.urls import path
from .views import may_calendar_view, available_boats_by_date

urlpatterns = [
    path('', may_calendar_view, name='may-calendar'),
    path('available-boats/', available_boats_by_date, name='available-boats'),
]