from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('',views.home_view, name='home'), 
    path('profile',views.profile, name='profile'), 
    path('profile/change_password/', views.change_password, name='change_password'),
]



