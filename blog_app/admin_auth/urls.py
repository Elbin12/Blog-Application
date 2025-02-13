from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.SignIn.as_view(), name='admin-signin'),
    path('home/', views.HomeView.as_view(), name='admin-home'),
    path('user-detail/<int:id>/', views.UserDetail.as_view(), name='user_detail'),
]