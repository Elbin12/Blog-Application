from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.generics import ListCreateAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView
from .models import CustomUser, UserProfile, Blog, Comments, Interactions
from .serializers import SignupSerializer, UserSerializer, UserProfileSerializer, BlogSerializer, InteractionSerializer, CommentsSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError   
import os
from .utils import upload_fileobj_to_s3, token_generation_and_set_in_cookie
from datetime import datetime
from django.contrib import messages

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
        try:
            blog = Blog.objects.get(id=id)
            serializer = BlogSerializer(blog, context={'request':request})
            return Response({'blog':serializer.data})
        except Blog.DoesNotExist:
            return Response({'error':'Blog not found.'}, status=401)
        
class UpdateInteractions(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Interactions.objects.all()
    serializer_class = InteractionSerializer

    def get_object(self):
        blog_id = self.request.data.get('blog_id')
        blog = Blog.objects.get(id=blog_id)
        interaction, created = Interactions.objects.get_or_create(user=self.request.user, blog=blog)
        return interaction
    

class CreateComment(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'blog_details.html'

    def post(self, request):
        blog_id = self.request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
            comment = request.POST.get('comment')
            if not comment:
                messages.error(request, "Please add a comment.")
                return redirect('blog-detail', id=blog.id)
            Comments.objects.create(blog=blog, user=request.user, comment=comment)
            messages.success(request, "Comment added successfully.")
            return redirect('blog-detail', id=blog.id)
        except Blog.DoesNotExist:
            return Response({'message':'Not found.'}, status=404)
        
class BlogList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'your_blogs.html'

    def get(self, request):
        blogs = Blog.objects.filter(user=request.user)
        serializer = BlogSerializer(blogs, many=True)
        return Response({'blogs':serializer.data})
    
class CreateBlog(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'create_blog.html'

    def get(self, request):
        return Response(status=200)

    def post(self, request):
        serializer = BlogSerializer(data=request.POST)
        
        if serializer.is_valid():
            image_path = None
            if 'image' in request.FILES:
                file = request.FILES['image']
                file_extension = os.path.splitext(file.name)[1]
                current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{current_time_str}{file_extension}"
                s3_file_path = f"users/blog/image/{unique_filename}"

                try:
                    upload_fileobj_to_s3(file, s3_file_path)
                    image_path = s3_file_path
                except Exception as e:
                    messages.error(request, f"Failed to upload image: {str(e)}")
                    return redirect('create-blog')
            else:
                messages.error(request, "Image is required")
                return redirect('create-blog')

            serializer.save(user=request.user, image=image_path)
            messages.success(request, "Blog post created successfully!")
            return redirect('your_blogs')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            return redirect('create-blog')
    
class EditBlog(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_blog.html'

    def get(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
            if request.user != blog.user:
                print('kkfkf')
                return Response({'message':'You donot have the permission to access.'}, status=404)
            serializer = BlogSerializer(blog)
            print('kkkk')
            return Response({'blog':serializer.data}, status=200)
        except Blog.DoesNotExist:
            return Response({'message':'Not found.'}, status=404)

    def post(self, request, id):
        print('kmlkmbf bfm ')
        blog = get_object_or_404(Blog, id=id)

        serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request':request})

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Blog updated successfully!")
            return self.get(request, id)
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            return redirect('edit-blog', id=blog.id)