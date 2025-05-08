from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),  # 수정: '' 빈 문자열로 변경
]
