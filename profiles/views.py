import os
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .models import User, VerifyUserEmail
from .serializers import UserRegistrationSerializer, OTPSerializer, ResetPasswordSerializer
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse, JsonResponse
from twilio.rest import Client
from .permissions import VerifiedUsersAccessOnly, PremiumUsersAccessOnly
from django.shortcuts import get_object_or_404


client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


class RegisterView(generics.CreateAPIView):
    """
    * User registration
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserRegistrationSerializer


class TestApiEndpointVerifiedUsers(generics.CreateAPIView):
    permission_classes = (VerifiedUsersAccessOnly,)

    def get(self, request):
        return Response({'message': 'Hello Verified user from Oauth2.0 ;)'}, status=status.HTTP_200_OK)


class TestApiEndpointPremiumUsers(generics.CreateAPIView):
    permission_classes = (PremiumUsersAccessOnly,)

    def get(self, request):
        return Response({'message': 'Hello Premium user from Oauth2.0 ;)'}, status=status.HTTP_200_OK)


class OTPView(generics.CreateAPIView):
    """
    * Password reset view.
    * Uses Twilio OTP Verify service
    * Recieves email -> queries for user with email -> extracts phone number ->
    * calls verify service
    * After the service is called the user should recieve the phone number
    * and verify it with another post request
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )

    def get_queryset(self, email):
        return get_object_or_404(User, email=email)

    def get(self, request, *args, **kwargs):

        email = request.query_params.get('email')
        users_with_email = self.get_queryset(email)
        user = OTPSerializer(users_with_email)
        # Twilio client
        client.verify.v2.services(os.environ['TWILIO_SERVICE_SID']).verifications.create(to='+1' + user.data['phone_number'], channel='sms')

        return HttpResponse('Send the OTP password')

    def post(self, request, *args, **kwargs):

        code = request.query_params.get('code')
        phone_number = request.query_params.get('phone')
        email = request.query_params.get('email')
        user = self.get_queryset(email)

        verification_check = client.verify \
            .v2 \
            .services(os.environ['TWILIO_SERVICE_SID']) \
            .verification_checks \
            .create(to='+1' + phone_number, code=code)

        temp_token = VerifyUserEmail.objects.get(user=user)
        temp_token.activate_token()

        if verification_check.status == 'approved':
            return JsonResponse({'token' : temp_token.token})

        return JsonResponse({'message' : 'Wrong code, please try again'})


class ResetPasswordView(generics.GenericAPIView):
    """
    * Reset Password View. It requires user email,
    * and a token. Token is used as a form of verification
    * so that the route is protected.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def get_queryset(self, email):
        return get_object_or_404(User, email=email)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        token = request.data.get('token')
        serializer = self.get_serializer(data=request.data)

        if not email or not token:
            return Response({'error': 'Email and token are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_queryset(email)

        try:
            temp_token = VerifyUserEmail.objects.get(user=user)
        except VerifyUserEmail.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

        if token != temp_token.token:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)

        # Set and save the new password
        user.set_password(serializer.validated_data['password'])
        user.save()
        # Set the user to the long token
        temp_token.deactivate_token()

        return Response({'success': 'Password reset successfully'}, status=status.HTTP_200_OK)
