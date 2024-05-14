from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserRegistrationSerializer
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse


class RegisterView(generics.CreateAPIView):
    """
    * User registration
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserRegistrationSerializer


class TestApiEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')
