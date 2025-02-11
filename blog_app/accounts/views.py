from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.generics import ListCreateAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView
from .models import CustomUser, UserProfile, Blog, Comments, Interactions
from .serializers import SignupSerializer, UserSerializer, UserProfileSerializer, BlogSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
import os
from .utils import upload_fileobj_to_s3, token_generation_and_set_in_cookie
from datetime import datetime

# Create your views here.


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile_list.html'

    def post(self, request):
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':'user created successfully.'})
        return Response({'form': serializer, 'errors': serializer.errors})


class SigninView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            print(user, 'user')
            if not user.check_password(password):
                return Response({'message': 'Invalid password'}, status=400)
            return token_generation_and_set_in_cookie(user)
        except CustomUser.DoesNotExist:
            return Response({'message':'User not found'}, status=404)
        
class HomeView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    def get(self, request):
        print( request.user, 'user____')
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response({'blogs':serializer.data})

class BlogDetailsView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'blog_details.html'

    def get(self, request, id):
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=id)
            serializer = BlogSerializer(blog)
            return Response({'blog':serializer.data})
        except Blog.DoesNotExist:
            return Response({'error':'Blog not found.'}, status=401)