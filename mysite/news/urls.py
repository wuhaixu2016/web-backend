from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('change/', views.change, name='change'),
    path('register/', views.register, name = 'register'),
    path('logout/', views.logout, name = 'logout'),
    path('show/video/<int:video_id>', views.video, name='video'),
    path('home/video/<int:video_id>', views.video, name='video'),
    path('show/<int:video_id>', views.show, name='show'),
]