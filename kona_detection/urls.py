from django.urls import path,include
from kona_detection import views

urlpatterns = [

    path('video/', views.run_model_video, name='run_model_video'),
    path('', views.run_model_live, name='run_model_live'),
    
]
