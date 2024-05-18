from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import VerifyUserEmail


CREATE_USER_URL = reverse('profiles:register')


class UserEndPointsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'email': 'test@squest.app',
            'password': 'P@ss123!',
            'password2': 'P@ss123!',
            'first_name': 'Michael',
            'last_name': 'Scott',
            'dob': '1999-01-01',
            'phone_number': '1231231666',
            'profile_img': ''
        }

    def test_user_registration_endpont(self):
        """
        * Test the user creation endpoint
        """
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        temp_user = get_user_model().objects.get(email=self.payload['email'])
        self.assertTrue(temp_user.check_password(self.payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_must_be_18_to_register(self):
        """
        * Test: users must be 18 to create an account
        """
        payload = {
            'email': 'test@squest.app',
            'password': 'P@ss123!',
            'password2': 'P@ss123!',
            'first_name': 'Michael',
            'last_name': 'Scott',
            'dob': '2020-01-15',
            'phone_number': '1231231666',
            'profile_img': ''
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_both_passwords_match(self):
        """
        * Test: passwords must match
        """
        payload = {
            'email': 'test@squest.app',
            'password': 'P@ss123!',
            'password2': 'password',
            'first_name': 'Michael',
            'last_name': 'Scott',
            'dob': '1999-01-15',
            'phone_number': '1231231666',
            'profile_img': ''
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_new_verify_email_is_created_on_registration(self):
        """
        * Test: check if new active token to verify user email is created on registration
        """
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        temp_user = get_user_model().objects.get(email=res.data['email'])
        temp_token = VerifyUserEmail.objects.get(user=temp_user)

        self.assertEqual(len(temp_token.token), 6)
        self.assertTrue(temp_token.is_active)
        self.assertEqual(temp_user, temp_token.user)
