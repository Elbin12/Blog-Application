
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view()),
    path('signin/', views.SigninView.as_view()),
    path('home/', views.HomeView.as_view()),
    path('blog/<int:id>/', views.BlogDetailsView.as_view(), name='blog-detail'),
    path('blog/interactions/', views.UpdateInteractions.as_view(), name=''),
    path('comment/create/', views.CreateComment.as_view(), name='comment-create'),
    path('blogs/', views.BlogList.as_view(), name='your_blogs'),
    path('blog/create/', views.CreateBlog.as_view(), name='create-blog'),
    path('blog/edit/<int:id>/', views.EditBlog.as_view(), name='edit-blog'),
]
    