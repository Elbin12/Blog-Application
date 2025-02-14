from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import CustomUser, Blog
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from django.contrib import messages
from accounts.utils import token_generation_and_set_in_cookie
from rest_framework.renderers import TemplateHTMLRenderer
from .serializers import UserDetailsSerializer
from accounts.serializers import BlogSerializer

# Create your views here.


class SignIn(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin/signin.html'

    def get(self, request):
        return Response(status=200)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        print('request.data', request.data)
        try:
            user = CustomUser.objects.get(email=email)
            print(user, 'user')
            if not user.is_superuser:
                messages.error(request, 'You donot have permission to access this page.')
                return redirect('admin-signin')
            if not user.check_password(password):
                messages.error(request, 'Invalid password')
                return redirect('admin-signin')
            response = token_generation_and_set_in_cookie(user)
            return response
        except CustomUser.DoesNotExist:
            print('jgjg')
            messages.error(request, 'User not found')
            return redirect('admin-signin')
        
class HomeView(APIView):
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin/home.html'

    def get(self, request):
        serializer = UserSerializer(CustomUser.objects.filter(is_superuser=False).order_by('date_joined'), many=True)
        context = {'users':serializer.data}
        return Response(context)
    

class UserDetail(APIView):
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin/user-detail.html'

    def get(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
            serializer = UserDetailsSerializer(user)
            context = {'user':serializer.data}
            return Response(context)
        except CustomUser.DoesNotExist:
            print('kjkd ')
            messages.error(request, 'user not found')
            return redirect('admin-home')
        except Exception as e:
            messages.error(request, 'Internal server error')
            return redirect('admin-home')
        
    def post(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
            user.is_active = False if user.is_active else True
            user.save()
            print('jjjgjg')
            return redirect('user_detail', id=id)
        except CustomUser.DoesNotExist:
            print('kjkd ')
            messages.error(request, 'user not found')
            return redirect('admin-home')
        except Exception as e:
            messages.error(request, 'Internal server error')
            return redirect('admin-home')

class BlogDetails(APIView):
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin/blog_details.html'

    def get(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            serializer = BlogSerializer(blog)
            context = {'blog':serializer.data}
            return Response(context)
        except Blog.DoesNotExist:
            return redirect('admin-home')
        except Exception as e:
            return redirect('admin-home')
        
    def post(self, request, id):
        print('kdkdkkd')
        try:
            blog = Blog.objects.get(id=id)
            blog.is_active = False if blog.is_active else True
            blog.save()
            return redirect('user_detail', blog.user.id)
        except Blog.DoesNotExist:
            return redirect('admin-home')
        except Exception as e:
            return redirect('admin-home')