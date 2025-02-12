from .serializers import UserSerializer

def auth_context(request):
    return {
        "is_authenticated": request.user.is_authenticated,
        "user": UserSerializer(request.user).data if request.user.is_authenticated else None,
    }