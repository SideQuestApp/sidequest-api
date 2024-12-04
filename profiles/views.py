import os
import json
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .models import User, VerifyUserEmail, WouldYouRatherQA
from quest.models import QuestNode
from .serializers import UserRegistrationSerializer, OTPSerializer, ResetPasswordSerializer, WouldYouRatherQASerializer
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse, JsonResponse
from twilio.rest import Client
from .permissions import VerifiedUsersAccessOnly, PremiumUsersAccessOnly
from django.shortcuts import get_object_or_404
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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


class CreateWouldYouRatherQA(generics.GenericAPIView):
    # ! The url for this view is inside quest urls
    """
    """

    permission_classes = (AllowAny, )
    queryset = WouldYouRatherQA.objects.all()
    serializer_class = WouldYouRatherQASerializer

    def get_queryset(self, user_pk, quest_pk):
        if user_pk:
            return get_object_or_404(User, pk=user_pk)
        else:
            return get_object_or_404(QuestNode,
                                     pk=quest_pk)

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = self.get_queryset(body['user_pk'], None)
        initial = body['initial']
        previous_quest = None
        if initial is False:
            previous_quest = self.get_queryset(None, body['quest_pk'])

        model = ChatOpenAI(model=user.chain.model)

        with open('el_locations.json', mode='r') as file_:
            locations = file_.readlines()
            locations = ''.join(locations)
        messages = [
            SystemMessage(content=f"You are a travel assistant. Your job is to create  would you\
                          rather questions that will help determin other agent what activities\
                           should be given to the user in order to have a great time. Your questions\
                           have two possible answers. An example response would be:\
                          Would you rather look at trees or explore history?;Look at trees;Explore history\
                          The use of ; is to easily later delimit your responses. Make sure you include them.\
                          For your input you will be given the previous activity as well as a list of\
                           potential activities in the area. If you are not given a previous activity that means\
                          it is their first quest.\
                          Your questions should be tailored towards\
                           possible activities. Create {10 if initial else 1} question{'s' if initial else ''}.\
                            In case where you are creating 10 question choices pairs at the end put a newline.\
                                This way I can split all the questions created and parse them with your ; delim.\
                                    Additionally I want you to ALWAYS take into account possibly including\
                                        Cat caffee and zap zone. Never have a question that makes you choose\
                                             one or the other."),
            HumanMessage(locations + '\n' + str(previous_quest))
        ]
        response = model.invoke(messages)
        if initial is False:
            question = response.content.split(';')[0]
            choice_1 = response.content.split(';')[1].strip()
            choice_2 = response.content.split(';')[2].strip()
            qa = WouldYouRatherQA.objects.create(
                question=question,
                choice_1=choice_1,
                choice_2=choice_2,
                user=user
            )
            serializer = WouldYouRatherQASerializer(qa, many=False)
        else:
            questions = response.content.split('\n')
            qas = []
            for q in questions:
                try:
                    question = q.split(';')[0]
                    choice_1 = q.split(';')[1]
                    choice_2 = q.split(';')[2]
                    qa = WouldYouRatherQA.objects.create(
                        question=question,
                        choice_1=choice_1,
                        choice_2=choice_2,
                        user=user
                    )
                    qas.append(qa)
                except IndexError:
                    print(q)
            serializer = WouldYouRatherQASerializer(qas, many=True)
        return Response(serializer.data)


class AnswerWouldYouRatherQA(generics.GenericAPIView):
    # ! The url for this view is inside quest urls
    """
    """
    permission_classes = (AllowAny, )
    queryset = WouldYouRatherQA.objects.all()
    serializer_class = WouldYouRatherQASerializer

    def get_queryset(self):
        return get_object_or_404(WouldYouRatherQA, pk=self.request.query_params.get('pk'))

    def post(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        queryset.answer = body['answer']
        queryset.save()
        serializer = WouldYouRatherQASerializer(queryset, many=False)

        return Response(serializer.data)


class GetWouldYouRatherQA(generics.GenericAPIView):
    # ! The url for this view is inside quest urls
    """
    """
    permission_classes = (AllowAny, )
    queryset = WouldYouRatherQA.objects.all()
    serializer_class = WouldYouRatherQASerializer

    def get_queryset(self, user_pk, qa_pk):
        if user_pk:
            return get_object_or_404(User, user=user_pk)
        elif qa_pk:
            return get_object_or_404(WouldYouRatherQA, pk=qa_pk)
        else:
            return WouldYouRatherQA.objects.all()

    def get(self, request, *args, **kwargs):
        qa_pk = request.query_params.get('qa_pk')
        user_pk = request.query_params.get('user_pk')
        queryset = self.get_queryset(user_pk, qa_pk)
        # When the qa_pk is used always single for rest always many
        serializer = WouldYouRatherQASerializer(queryset, many=False if qa_pk else True)
        return Response(serializer.data)
