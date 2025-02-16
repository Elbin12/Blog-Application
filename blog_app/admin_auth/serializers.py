from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateTimeField
from accounts.models import CustomUser, UserProfile, Comments, Blog, Interactions
from accounts.utils import create_presigned_url
from django.utils.timesince import timesince
from datetime import datetime

class UsersProfileSerializer(ModelSerializer):
    profile_pic = SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'profile_pic']

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            image_url = create_presigned_url(str(obj.profile_pic))
            if image_url:
                print(image_url, 'll')
                return image_url
        return None

class UserDetailsSerializer(ModelSerializer):
    user_blog = SerializerMethodField()
    blog_count = SerializerMethodField()
    user_profile = UsersProfileSerializer()
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_active', 'date_joined', 'user_profile', 'user_blog', 'blog_count']
    
    def get_blog_count(self, obj):
        return obj.user_blog.count()
    
    def get_user_blog(self, obj):
        blogs = obj.user_blog.all().order_by('-created_at')
        return BlogSerializer(blogs, many=True).data
    
class UserSerializer(ModelSerializer):
    user_profile = SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_active', 'date_joined', 'user_profile', 'is_superuser']

    def get_user_profile(self, obj):
        user_profile = getattr(obj, 'user_profile', None)
        return UsersProfileSerializer(user_profile).data if user_profile else None


class CommentsSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    created_at = DateTimeField(format="%b %d, %Y %I:%M %p")
    time_ago = SerializerMethodField()
    class Meta:
        model = Comments
        fields = ['id', 'comment', 'created_at', 'user', 'time_ago', 'is_active']
        read_only_fields = ['blog', 'user']

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " ago"

class BlogSerializer(ModelSerializer):
    image = SerializerMethodField()
    user = UserSerializer(read_only=True)
    comments = CommentsSerializer(source='blog_comment', many=True, read_only=True)
    comments_count = SerializerMethodField()
    is_disliked = SerializerMethodField()
    like_count = SerializerMethodField()
    unlike_count = SerializerMethodField()
    created_at = DateTimeField(format="%b %d, %Y", read_only=True)
    class Meta:
        model = Blog
        fields = ['id', 'user', 'heading', 'sub_heading', 'body', 'image', 'like_count', 'unlike_count', 'created_at', 'updated_at', 'user', 'comments', 'comments_count', 'is_disliked', 'is_available', 'is_active']
        read_only_fields = ['user', 'like_count', 'unlike_count', 'created_at', 'updated_at', 'image', 'comments',]

    def get_like_count(self, obj):
        return Interactions.objects.filter(blog=obj, is_liked=True).count()
    
    def get_unlike_count(self, obj):
        return Interactions.objects.filter(blog=obj, is_disliked=True).count()

    
    def get_is_disliked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        interaction = Interactions.objects.filter(user=request.user, blog=obj).first()
        return interaction.is_disliked if interaction else None

    def get_image(self, obj):
        image_url = create_presigned_url(str(obj.image))
        if image_url:
            print(image_url, 'll')
            return image_url
        return None
    
    def get_comments_count(self, obj):
        return obj.blog_comment.count()