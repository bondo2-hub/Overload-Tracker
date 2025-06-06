from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('new-overload/', views.create_overload, name='new_overload'),
    path('progress/', views.progress, name='progress'),
    path('settings/', views.settings, name='settings'),
]
