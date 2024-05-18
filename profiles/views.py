from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserRegistrationSerializer
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse, JsonResponse
from twilio.rest import Client
import os


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


class ResetPasswordView(generics.CreateAPIView):
    """
    * Password reset view. 
    * Uses Twilio OTP Verify service
    * Recieves email -> queries for user with email -> extracts phone number ->
    * calls verify service
    * After the service is called the user should recieve the phone number
    * and verify it with another post request
    """
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):

        email = request.query_params.get('email')
        users_with_email = User.objects.filter(email=email)
        user = UserRegistrationSerializer(users_with_email, many=True)

        # Twilio client
        client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

        client.verify.v2.services(os.environ['TWILIO_SERVICE_SID']).verifications.create(to='+1' + user.data[0]['phone_number'], channel='sms')
