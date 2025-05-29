from django.urls import path
from . import views

urlpatterns = [
    path('', views.sediment_map_view, name='sediment_map'),
    path('run_simulation/', views.run_simulation, name='run_simulation'),  # 시뮬레이션 POST 처리용
]