from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mob=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            email = email,
            mob = mob,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mob=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, mob, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    mob = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions', 
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    first_name = models.CharField()
    last_name = models.CharField()
    profile_pic = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Blog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_blog')
    heading = models.CharField(max_length=150)
    sub_heading = models.CharField(max_length=100)
    body = models.TextField()
    image = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)

class Interactions(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_interactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_interactions')
    is_liked = models.BooleanField(default=False)
    is_disliked = models.BooleanField(default=False)
    

class Comments(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_comment')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_comment')
    comment = models.TextField()
    like_count = models.IntegerField(default=0)
    unlike_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)