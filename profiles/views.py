from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserRegistrationSerializer


class RegisterView(generics.CreateAPIView):
    """
    * User registration
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserRegistrationSerializer
