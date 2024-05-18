from datetime import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.response import Response
from django.db import IntegrityError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from .models import User, VerifyUserEmail


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    * Serializer for user registration
    * Match password and verify password
    * Validate email
    """
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator(message="Email must be valid"),
        ]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password,])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2',
                  'first_name', 'last_name', 'dob',
                  'phone_number', 'profile_img')

    def validate(self, attrs):
        """
        * Check passwords match
        * Validate email
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'error': 'Passwords do not match'})

        # Check if the user is 18+
        dob = datetime.strptime(attrs['dob'], '%Y-%m-%d').date()
        today = now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise serializers.ValidationError({'error': 'You must be at least 18 years old.'})

        return attrs

    def create(self, validated_data):
        """
        * Creates an User instance with validated data
        """
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            dob=validated_data['dob'],
            phone_number=validated_data['phone_number'],
            profile_img=validated_data['profile_img'],
        )

        user.set_password(validated_data['password'])
        user.save()

        try:
            verify_email_token = VerifyUserEmail.objects.create(user=user)
            verify_email_token.save()
        except IntegrityError as e:
            return Response({'error': e})

        return user


class OTPSerializer(serializers.Serializer):
    """
    * Serializer for the OTP Reset Password Workflow.
    * We only need the phone number of the user to send the OTP
    """
    phone_number = serializers.CharField(read_only=True)


class ResetPasswordSerializer(serializers.Serializer):
    """

    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password,])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """
        * Check passwords match
        * Validate email
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'error': 'Passwords do not match'})
        return attrs
