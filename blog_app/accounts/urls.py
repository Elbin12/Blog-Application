
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view()),
    path('signin/', views.SigninView.as_view()),
    path('home/', views.HomeView.as_view()),
    path('blog/<int:id>/', views.BlogDetailsView.as_view(), name='blog_detail'),
]
    