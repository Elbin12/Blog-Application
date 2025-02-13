from rest_framework.serializers import ModelSerializer, SerializerMethodField
from accounts.models import CustomUser, UserProfile
from accounts.utils import create_presigned_url
from accounts.serializers import BlogSerializer

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
    user_blog = BlogSerializer(many=True)
    blog_count = SerializerMethodField()
    user_profile = UsersProfileSerializer()
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_active', 'date_joined', 'user_profile', 'user_blog', 'blog_count']
    
    def get_blog_count(self, obj):
        return obj.user_blog.count()