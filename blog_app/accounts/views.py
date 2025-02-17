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
from django.core.paginator import Paginator

# Create your views here.


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    def post(self, request):
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Signup successfully.')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect('home')


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
        blogs = Blog.objects.filter(is_available=True, is_active=True)
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
        paginator = Paginator(blogs, 2)
        page_number = request.GET.get('page')
        blogs = paginator.get_page(page_number)
        serializer = BlogSerializer(blogs, many=True)
        return Response({
            'blogs': serializer.data,  
            'page_number': blogs.number,
            'has_previous': blogs.has_previous(),
            'has_next': blogs.has_next(),
            'previous_page': blogs.previous_page_number() if blogs.has_previous() else None,
            'next_page': blogs.next_page_number() if blogs.has_next() else None,
            'total_pages': paginator.num_pages
        })
    
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

            serializer.save(user=request.user, image=image_path, is_active=True, is_available=True  )
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
        
class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            print(refresh_token, 'resfreesh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response(status=200)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            response.delete_cookie('csrftoken')
            return response
        except Exception as e:
            print(e, 'ee')
            return Response(status=400)
        
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile_page.html'

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not first_name:
            messages.error(request, 'Please fill first name.')
            return redirect('profile')
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

class ProfilePicUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print(request.data, 'data')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request':request})

        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Profile image updated successfully.')
            return redirect('profile')
        
        messages.error(request, serializer.errors)
        return redirect('profile')