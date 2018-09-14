from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('change/', views.change, name='change'),
    path('register/', views.register, name = 'register'),
    path('logout/', views.logout, name = 'logout'),

    path('home/video/<int:video_id>', views.video, name='video'),
    path('alarm/<int:video_id>', views.showAlarm, name='alarm'),

    path('show/video/<int:video_id>', views.alarm, name='video'),
    path('show/delete_all/<int:video_id>', views.deleteall, name='deleteall'),
    path('show/<int:video_id>', views.show, name='show'),
    path('show/alarm/<int:video_id>', views.showAlarm, name='showAlarm'),

    path('delete_all/<int:video_id>', views.deleteall, name='deleteall'),
    path('delete/<int:alarm_id>/<int:video_id>', views.delete, name='delete'),

    path('changeChannel/<int:video_id>', views.changeChannel, name='changeChannel'),
    path('changeChannel/video/<int:video_id>', views.alarm, name='video'),
    path('changeChannel/alarm/<int:video_id>', views.showAlarm, name='showAlarm'),
    path('changeChannel/delete_all/<int:video_id>', views.deleteall, name='deleteall'),
]