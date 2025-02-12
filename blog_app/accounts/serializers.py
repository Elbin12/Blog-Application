from rest_framework.serializers import ModelSerializer, ValidationError, FileField, SerializerMethodField, DateTimeField
from .models import CustomUser, UserProfile, Blog, Comments, Interactions
import os
from datetime import datetime
from .utils import create_presigned_url, upload_fileobj_to_s3
from django.utils.timesince import timesince


class SignupSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user
    
class UserProfileSerializer(ModelSerializer):
    profile_pic = SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'profile_pic']
        read_only_fields = ['id', 'user', 'profile_pic']
        extra_kwargs = {
            'profile_pic': {'required': False},
        }

    def get_profile_pic(self, obj):
        if obj.profile_pic:
            image_url = create_presigned_url(str(obj.profile_pic))
            if image_url:
                print(image_url, 'll')
                return image_url
        return None

    def validate(self, value):
        if isinstance(value, FileField):
            raise ValidationError("Direct file upload is not supported here.")
        return value

    def update(self, instance, validated_data):
        if 'profile_pic' in self.context['request'].FILES:
            file = self.context['request'].FILES['profile_pic']
            
            file_extension = os.path.splitext(file.name)[1]
            current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{current_time_str}{file_extension}"
            s3_file_path = f"users/profile_pic/{unique_filename}"

            try:
                upload_fileobj_to_s3(file, s3_file_path)
                validated_data['profile_pic'] = s3_file_path
            except Exception as e:
                raise ValidationError(f"File upload failed: {str(e)}")

        return super().update(instance, validated_data)

class UserSerializer(ModelSerializer):
    user_profile = UserProfileSerializer()
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_active', 'date_joined', 'user_profile', 'is_superuser']


class CommentsSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    created_at = DateTimeField(format="%b %d, %Y %I:%M %p")
    time_ago = SerializerMethodField()
    class Meta:
        model = Comments
        fields = ['id', 'comment', 'created_at', 'user', 'time_ago']
        read_only_fields = ['blog', 'user']

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " ago"

class BlogSerializer(ModelSerializer):
    image = SerializerMethodField()
    user = UserSerializer(read_only=True)
    comments = CommentsSerializer(source='blog_comment', many=True, read_only=True)
    comments_count = SerializerMethodField()
    is_liked = SerializerMethodField()
    is_disliked = SerializerMethodField()
    like_count = SerializerMethodField()
    unlike_count = SerializerMethodField()
    created_at = DateTimeField(format="%b %d, %Y", read_only=True)
    class Meta:
        model = Blog
        fields = ['id', 'user', 'heading', 'sub_heading', 'body', 'image', 'like_count', 'unlike_count', 'created_at', 'updated_at', 'user', 'comments', 'comments_count', 'is_liked', 'is_disliked', 'is_available']
        read_only_fields = ['user', 'like_count', 'unlike_count', 'created_at', 'updated_at', 'image', 'comments',]

    def get_like_count(self, obj):
        return Interactions.objects.filter(blog=obj, is_liked=True).count()
    
    def get_unlike_count(self, obj):
        return Interactions.objects.filter(blog=obj, is_disliked=True).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        interaction = Interactions.objects.filter(user=request.user, blog=obj).first()
        return interaction.is_liked if interaction else None
    
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
    
    def update(self, instance, validated_data):
        if 'image' in self.context['request'].FILES:
            file = self.context['request'].FILES['image']
            
            file_extension = os.path.splitext(file.name)[1]
            current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{current_time_str}{file_extension}"
            s3_file_path = f"users/blog/image/{unique_filename}"

            try:
                upload_fileobj_to_s3(file, s3_file_path)
                validated_data['image'] = s3_file_path
            except Exception as e:
                raise ValidationError(f"File upload failed: {str(e)}")

        return super().update(instance, validated_data)
    
class InteractionSerializer(ModelSerializer):
    like_count = SerializerMethodField()
    unlike_count = SerializerMethodField()
    class Meta:
        model = Interactions
        fields = ['is_liked', 'is_disliked', 'like_count', 'unlike_count']

    def get_like_count(self, obj):
        return Interactions.objects.filter(blog=obj.blog, is_liked=True).count()
    
    def get_unlike_count(self, obj):
        return Interactions.objects.filter(blog=obj.blog, is_disliked=True).count()